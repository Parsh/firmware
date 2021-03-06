import uerrno as errno

class USB_VCP:
    @staticmethod
    def isconnected():
        return True

    @staticmethod
    def any():
        return False

global _umode
_umode = None
def usb_mode(nm=None, **kws):
    global _umode
    if nm:
        _umode = nm
    return _umode

class USB_HID:
    def __init__(self):
        import sys
        import usocket as socket
        fn = b'/tmp/ckcc-simulator.sock'
        self.pipe = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        addr = bytes([len(fn)+2, socket.AF_UNIX] + list(fn))
        # If on linux, try uncommenting the following two lines
        #import struct
        #addr = struct.pack('H108s', socket.AF_UNIX, fn)
        while 1:
            try:
                self.pipe.bind(addr)
                break
            except OSError as exc:
                if exc.args[0] == errno.EADDRINUSE:
                    # handle restart after first run
                    import os
                    os.unlink(fn)
                    continue
        
    def recv(self, buf, timeout=0):
        # recv-into, with from...
        if isinstance(buf, int):
            # can work in-place, or create buffer
            my_alloc = True
            maxlen = buf
        else:
            my_alloc = False
            maxlen = len(buf)

        if not timeout:
            self.pipe.setblocking(1)
            msg, frm = self.pipe.recvfrom(maxlen)
        else:
            self.pipe.setblocking(0)
            try:
                msg, frm = self.pipe.recvfrom(maxlen)
            except OSError as exc:
                if exc.args[0] == errno.EAGAIN:
                    return None if my_alloc else 0

        self.last_from = frm
        assert frm[2] != b'\0', "writer must bind to a name"

        #print("Rx[%d]: %r (from %r)" % (len(msg), msg, frm))

        if my_alloc:
            return msg
        else:
            buf[0:len(msg)] = msg
            return len(msg)

    def send(self, buf):
        try:
            return self.pipe.sendto(buf, self.last_from)
        except OSError as exc:
            if exc.args[0] == errno.ENOENT:
                # caller is gone
                return None

    def _test(self):
        b = bytearray(64)
        while 1:
            count = self.recv(b)
            print("Tx[%d]: %r (from %r)" % (count, b, self.last_from))
            self.send(b)

class SDCard:
    @staticmethod
    def present():
        #return False
        return True

    @staticmethod
    def power(st=0):
        return False

class Pin:
    PULL_NONE =1
    PULL_UP =2
    
    def __init__(self, *a, **kw):
        return

class ExtInt:
    def __init__(self, *a, **kw):
        return

    IRQ_RISING = 1
    IRQ_RISING_FALLING = 2
