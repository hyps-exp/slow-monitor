import socket
import serial
import threading
import queue
import signal
import sys
import logging
import time

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
  handlers=[logging.StreamHandler(sys.stdout)]
)

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
host = '127.0.0.1'
port = 5000

request_queue = queue.Queue()
response_queues = {}
running = True

def signal_handler(sig, frame):
  global running
  logging.info("Shutting down server...")
  running = False
  request_queue.put((None, "STOP"))
  ser.close()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def process_requests():
  while running:
    client_id, command = request_queue.get()
    if command == "STOP":
      break
    ser.write((command + '\r\n').encode())
    time.sleep(0.001)
    response = ser.read_until(b'\r\n').decode().strip()
    if client_id in response_queues:
      response_queues[client_id].put(response)
    request_queue.task_done()

def handle_client(conn, addr):
  client_id = addr
  response_queues[client_id] = queue.Queue()
  with conn:
    logging.info(f"Connected by {addr}")
    while running:
      data = conn.recv(1024).decode().strip()
      if not data:
        break
      logging.info(f"Received command from {addr}: {data}")
      request_queue.put((client_id, data))
      response = response_queues[client_id].get()
      conn.sendall((response + '\n').encode())
      logging.info(f"Sent response to {addr}: {response}")
  del response_queues[client_id]
  logging.info(f"Connection with {addr} closed.")

def start_server():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    logging.info(f"Server listening on {host}:{port}")
    threading.Thread(target=process_requests, daemon=True).start()
    while running:
      conn, addr = s.accept()
      client_thread = threading.Thread(target=handle_client, args=(conn, addr))
      client_thread.start()

if __name__ == "__main__":
  try:
    start_server()
  finally:
    ser.close()
    logging.info("Serial port closed.")
