from r2a.ir2a import IR2A
from player.parser import *
import time


class R2ANewAlgorithm1(IR2A):

    ALPHA = 0.5
    NU = 0.3

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.request_time = 0
        self.qi = []
        self.actual_qi_position = 0
        self.download_time = 1
        self.Qwk = []
        self.length = 1

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.request_time = time.perf_counter()

        q_estimated = self.qi[self.actual_qi_position]*self.length/self.download_time
        gain = self.ALPHA * (q_estimated - self.qi[self.actual_qi_position])


        Dwk = 0
        for q in range(len(self.qi)):
            if self.qi[q] != self.qi[self.actual_qi_position]:
                self.Qwk.append( self.qi[q]/(abs(self.qi[q] - self.qi[self.actual_qi_position])) )
                Dwk += abs(self.qi[q] - self.qi[self.actual_qi_position])

        next_qi = self.qi[self.actual_qi_position] + self.NU * (gain - sum(self.Qwk) * (1/Dwk))

        for q in range(len(self.qi)):
            if self.qi[q] <= next_qi:
                self.actual_qi_position = q


        msg.add_quality_id(self.qi[self.actual_qi_position])
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.length = msg.get_segment_size()
        self.download_time = t
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
