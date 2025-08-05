import cv2
import time
from typing import Dict, Any

class Camera:
    """
    Camera functionality for capturing images
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def capture_image(self, image_path: str = "captured_image.jpg") -> bool:
        """
        Capture an image from the camera
        """
        try:
            cap = cv2.VideoCapture(self.config.get("camera_device_index", 0))
            
            # Check if camera opened successfully
            if not cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Allow camera to warm up and adjust
            # Read a few frames to let the camera adjust exposure and focus
            warmup_frames = self.config.get("camera_warmup_frames", 5)
            warmup_delay = self.config.get("camera_warmup_delay", 0.1)
            for i in range(warmup_frames):  # Skip first 5 frames
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame from camera")
                    cap.release()
                    return False
                time.sleep(warmup_delay)  # Small delay between frames
            
            # Capture the actual frame
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(image_path, frame)
                cap.release()
                return True
            else:
                print("Error: Could not capture frame")
                cap.release()
                return False
                
        except Exception as e:
            print(f"Error capturing image: {e}")
            try:
                cap.release()
            except:
                pass
            return False