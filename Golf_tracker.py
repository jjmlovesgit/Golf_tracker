import os
from dotenv import load_dotenv  # Load .env files
import cv2                      # OpenCV for image and video processing & drawing
import numpy as np              # NumPy for math and array handling pixel arrays
import gradio as gr             # Gradio for UI
import vision_agent.tools as T  # VisionAgent SDK for AI-based object tracking
import logging                  # Logging 

# ====================================
# 🔐 Load Environment & API Key Setup
# ====================================
load_dotenv()
VISION_AGENT_API_KEY = os.getenv("VISION_AGENT_API_KEY")

if not VISION_AGENT_API_KEY:
    raise ValueError(
        "❌ VISION_AGENT_API_KEY not found in environment variables.\n"
        "Get your API key here: https://va.landing.ai/settings/api-key\n"
        "Then set it in a .env file or as an environment variable."
    )

# Suppress irrelevant asyncio warnings on Windows 
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# ============================
# 🧮 Utility: Numpy Euclidean Distance (distance between two points)
# ============================
def calculate_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# =====================================================
# 🧹 Filter frames for those containing a moving ball - noise reduction
# =====================================================
def filter_moving_objects(tracks, confidence_thresh, move_thresh):
    filtered_tracks = []
    previous_positions = {}

    for detections in tracks:
        current_frame_detections = []
        # Filtering for low confidence
        for det in detections:
            if det.get("score", 0) < confidence_thresh:
                continue
            # Bounding box center - {x,y} location
            xmin, ymin, xmax, ymax = det["bbox"]
            center = ((xmin + xmax) / 2, (ymin + ymax) / 2)
            label = det["label"]
            moved = True
            # Checks for static objects – do not track static ones 
            if label in previous_positions:
                if calculate_distance(center, previous_positions[label]) < move_thresh:
                    moved = False
            # If it has moved – track it
            if moved:
                previous_positions[label] = center
                current_frame_detections.append(det)
            # Add moving object detections to our output list
        filtered_tracks.append(current_frame_detections)

    return filtered_tracks

# ===================================================
# 🎥 Main Processing Function Orchestration for our video
# 1. Extracts frames from the input video
# 2. Tracks objects across frames using LandingAI's vision agent tools
# 3. Filters noisy or non-moving detections
# 4. Annotates movement with a fading trace line
# 5. Saves the final annotated video

def process_video(uploaded_video_file, output_fps=15,
                 movement_thresh=0.01, confidence_thresh=0.8, trace_tail_len=25):
    
    # These flags are used to indicate progress through each stage of processing
    flags = [False] * 5 #Processing Steps in UI
    video = None  # Final output path

    try:
        # 🚫 Safety check: Make sure a video file was uploaded
        if uploaded_video_file is None:
            print("❌ No video uploaded.")
            yield video, *flags #update UI as we go
            return

        # Default object label and UI toggle (can be expanded for other labels later)
        object_label = "Ball" # i.e., what we are tracking
        show_trace = True

        # 🔐 Ensure API key is available (defensive check)
        if not VISION_AGENT_API_KEY:
            raise ValueError("VisionAgent API key not available during processing")

        # 🛠️ Prepare input and output paths
        input_path = uploaded_video_file.name
        temp_dir = os.path.join(os.path.dirname(input_path), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        output_path = os.path.join(temp_dir, "annotated_output.mp4")

        # ============================================================
        # ✅ Step 1: Extract frames from the video at a given FPS
        # LandingAI returns frames and timestamps. 
        # ============================================================
        frames_and_ts = T.extract_frames_and_timestamps(input_path, fps=output_fps)
        frames = [f["frame"] for f in frames_and_ts]
        if not frames:
            print("❌ No frames extracted!")
            yield video, *flags
            return
        flags[0] = True
        yield video, *flags  # Update UI or pipeline that frames were extracted

        # ============================================================
        # 🎯 Step 2: Use LandingAI to find the object (label="Ball") in frames
        # This uses the Florence2 model from VisionAgent
        # ============================================================
        raw_tracks = T.florence2_sam2_video_tracking(object_label, frames)
        flags[1] = True
        yield video, *flags  # Update: Object tracking completed

        # ============================================================
        # 🔍 Step 3: Filter out stationary or low-confidence detections
        # This removes noise and focuses only on confidently moving objects
        # ============================================================
        filtered_tracks = filter_moving_objects(raw_tracks, confidence_thresh, movement_thresh)
        flags[2] = True
        yield video, *flags  # Update: Filtering complete

        # ============================================================
        # 🖍️ Step 4: Annotate each frame
        # Draw the object's movement as a trace line using fading alpha
        # ============================================================
        annotated_frames = []
        ball_trace = []  # Stores center points for the trace path

        # Focus on the moving detections; make a copy for annotation with the trace...
        for frame, detections in zip(frames, filtered_tracks):
            annotated_frame = frame.copy()

            # For each detection, compute the center point and add coordinates to trace list 
            for det in detections:
                xmin, ymin, xmax, ymax = det["bbox"]
                center_x = int((xmin + xmax) / 2 * frame.shape[1])
                center_y = int((ymin + ymax) / 2 * frame.shape[0])
                ball_trace.append((center_x, center_y))

            # If we have more than one trace point, draw fading trail using exponential alpha fade
            if show_trace and len(ball_trace) > 1:
                trace_overlay = annotated_frame.copy()
                trace_points = np.array(ball_trace[-trace_tail_len:], dtype=np.int32)

                # Create alpha values that fade older points (math for exponential decay)
                alphas = np.exp(-0.2 * np.arange(trace_tail_len, 0, -1))

                # Draw each trace point as a fading circle using an alpha value with OpenCV
                for i, (x, y) in enumerate(trace_points):
                    circle_overlay = trace_overlay.copy()
                    cv2.circle(circle_overlay, (x, y), 4, (255, 165, 0), -1)  # Orange circle
                    cv2.addWeighted(circle_overlay, alphas[i], trace_overlay, 1 - alphas[i], 0, trace_overlay)

                # Use overlay with fading circles as the final annotated frame
                annotated_frame = trace_overlay

            # Add finished frame to the list
            annotated_frames.append(annotated_frame)

        flags[3] = True
        yield video, *flags  # Update IU: Frame annotation complete

        # ============================================================
        # 💾 Step 5: Save the final annotated video
        # Write frames to an mp4 video using the VisionAgent helper
        # ============================================================
        T.save_video(annotated_frames, output_path, fps=output_fps)
        video = output_path
        flags[4] = True
        yield video, *flags  # Update UI: Video successfully saved

    # ============================================================
    # 🚨 Error Handling: Gracefully catch and report any exceptions
    # API-specific issues remain the focus -- i.e. expired key?
    # ============================================================
    except Exception as e:
        if "API" in str(e):
            print(f"""
            ❌ VisionAgent API Error: {e}
            Please verify your API key is correct and active.
            Get your key here: https://va.landing.ai/settings/api-key
            Current key: {VISION_AGENT_API_KEY[:5]}... (first 5 chars)
            """)
        else:
            print(f"❌ Error: {e}")
        yield video, *flags


# =============================
# 🧼 Reset Outputs and UI for New Input
# =============================
def reset_outputs(file):
    return (
        file.name if file else None,
        None,
        False, False, False, False, False
    )

# ===================
# 📦 Gradio UI Layout - upload, sliders, viewers, "Process Button"
# ===================
with gr.Blocks(title="Golf Ball Tracker") as demo:
    gr.Markdown("""
    # 🏌️ Golf Ball Tracker with a Fading Tracer
    **API Key Required:** [Get your VisionAgent API key](https://va.landing.ai/settings/api-key)
    """)
    gr.Markdown("Upload a golf swing video and track the **moving ball** with optional motion trail.")

    with gr.Row():
        with gr.Column():
            video_input = gr.File(label="📂 Video", file_types=[".mp4"])
            video_preview = gr.Video(label="Uploaded Video Preview", interactive=False)
            submit_btn = gr.Button("Process Video")

            with gr.Accordion(label="⚙️ Advanced Settings", open=False):
                with gr.Row():
                    with gr.Column():
                        fps_slider = gr.Slider(minimum=1, maximum=30, value=15, label="Output FPS")
                        movement_thresh_slider = gr.Slider(
                            minimum=0.001,
                            maximum=0.05,
                            value=0.001,
                            step=0.001,
                            label="Motion Sensitivity (lower = more sensitive)"
                        )
                    with gr.Column():
                        confidence_thresh_slider = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.99,
                            step=0.01,
                            label="Min Detection Confidence (0 = accept all, 1 = very strict)"
                        )
                        trace_tail_slider = gr.Slider(
                            minimum=5,
                            maximum=100,
                            value=30,
                            step=1,
                            label="Trace Tail Length"
                        )

        with gr.Column():
            video_output = gr.Video(label="Processed Output")

            frame_status = gr.Checkbox(label="✅ Frames Extracted", value=False, interactive=False)
            tracking_status = gr.Checkbox(label="✅ Object Tracking Complete", value=False, interactive=False)
            filter_status = gr.Checkbox(label="✅ Movement Filter Applied", value=False, interactive=False)
            annotation_status = gr.Checkbox(label="✅ Frames Annotated", value=False, interactive=False)
            save_status = gr.Checkbox(label="✅ Video Saved", value=False, interactive=False)

    video_input.change(
        fn=reset_outputs,
        inputs=video_input,
        outputs=[
            video_preview,
            video_output,
            frame_status,
            tracking_status,
            filter_status,
            annotation_status,
            save_status
        ]
    )
    # Connects processing button to our main function and captures output to the UI
    submit_btn.click(
        fn=process_video,
        inputs=[
            video_input,
            fps_slider,
            movement_thresh_slider,
            confidence_thresh_slider,
            trace_tail_slider
        ],
        outputs=[
            video_output,
            frame_status,
            tracking_status,
            filter_status,
            annotation_status,
            save_status
        ]
    )

# ================
# 🚀 Run the App
# ================
if __name__ == "__main__":
    try:
        demo.launch(share=False) #starts Gradio
    except KeyboardInterrupt:
        print("🛑 Server manually stopped by user.")
    except ConnectionResetError:
        print("⚠️ Connection was reset by browser, safe to ignore.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")



        print(f"❌ An error occurred: {e}")
