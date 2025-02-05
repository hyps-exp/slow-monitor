import logging
import socket
import time

logger = logging.getLogger('__main__').getChild(__name__)
# logging.basicConfig(level=logging.DEBUG)

#______________________________________________________________________________
class PMX_A():
  PORT = 5025 # fixed

  #____________________________________________________________________________
  def __init__(self, host, timeout=0.1, debug=False):
    self.host = host
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug('host = {}'.format(self.host))
    logger.debug('port = {}'.format(self.PORT))
    self.sock.settimeout(timeout)
    self.debug = debug
    try:
      self.sock.connect((self.host, self.PORT))
      self.is_open = True
      logger.debug('connected')
    except (socket.error, socket.timeout):
      self.is_open = False
      logger.debug('failed')
  #____________________________________________________________________________
  def __del__(self):
    if self.is_open:
      self.sock.close()

  #____________________________________________________________________________
  def __read(self, rlen=1024):
    if self.is_open:
      try:
        data = self.sock.recv(rlen).decode().strip()
        if self.debug:
          logger.debug(f'R: {data}')
        return data
      except socket.timeout:
        return ''

  #____________________________________________________________________________
  def __write(self, data, readback=False):
    if self.is_open and len(data) > 0:
      if self.debug:
        logger.debug(f'W: {data}')
      data += '\n'
      self.sock.send(data.encode())
    if readback:
      time.sleep(0.02)
      return self.__read()

  #____________________________________________________________________________
  def curr(self, arg=None):
    if arg is None:
      return float(self.__write('MEAS:CURR?', True))
    else:
      self.__write(f'CURR {arg}')

  #____________________________________________________________________________
  def idn(self):
    return self.__write('*IDN?', True)

  #____________________________________________________________________________
  def interactive(self):
    while True:
      try:
        data = input('>> ')
      except (KeyboardInterrupt, EOFError) as e:
        logger.error(e)
        break
      if data == 'q' :
        break
      self.__write(data, readback=True)

  #____________________________________________________________________________
  def keylock(self, lock=1):
    return self.__write(f'SYST:KLOC {lock}')

  #____________________________________________________________________________
  def outp(self, arg=None):
    if arg is None:
      return int(self.__write('OUTP?', True))
    else:
      self.__write(f'OUTP {arg}')

  #____________________________________________________________________________
  def rst(self):
    return self.__write('*RST')

  #____________________________________________________________________________
  def stat(self):
    return (int(self.__write('STAT:OPER:COND?', True)),
            int(self.__write('STAT:QUES:COND?', True)))

  #____________________________________________________________________________
  def volt(self, arg=None):
    if arg is None:
      return float(self.__write('MEAS:VOLT?', True))
    else:
      self.__write(f'VOLT {arg}')
      # self.__write(f'VOLT:PROT {arg*1.1}')

#______________________________________________________________________________
if __name__ == '__main__':
  hosts = ['kikusui1']
  for host in hosts:
    pmxa = PMX_A(host, timeout=1.0, debug=True)
    if not pmxa.is_open:
      continue
    idn = pmxa.idn()
    vmon = pmxa.volt()
    imon = pmxa.curr()
    outp = pmxa.outp()
    stat = pmxa.stat()
    print(f'kikusui,host={host} vmon={vmon},imon={imon},outp={outp}i,'+ # idn=\"{idn}\"
          f'operation_status={stat[0]}i,questionable_status={stat[1]}i')
  #pmxa.interactive()
