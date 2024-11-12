import cv2
import time
import os
import sys

save_dir = '/misc/subdata/tmp'

def capture_snapshot(rtsp_url, output_file, interval=1):
  cap = cv2.VideoCapture(rtsp_url)
  if not cap.isOpened():
    print(f'Cannot connect RTSP stream: {rtsp_url}')
    return False

  try:
    while True:
      ret, frame = cap.read()
      if not ret:
        print('Failed to capture')
        cap.release()
        break
      frame = cv2.resize(frame, (960, 640))
      cv2.imwrite(output_file, frame)
      print(f'Save snapshot: {output_file}')
      time.sleep(interval)
  except KeyboardInterrupt:
    print()
  finally:
    cap.release()

if __name__ == '__main__':
  if len(sys.argv) < 2:
    exit
  host = sys.argv[1]
  rtsp_url = f'rtsp://admin:beamtime@{host}/stream1'
  output_file = os.path.join(save_dir, f'{host}.png')
  capture_snapshot(rtsp_url, output_file, 10)
