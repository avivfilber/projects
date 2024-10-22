"""
Author:
Aviv Filber - 206360257
"""
class Packet:
    def __init__(self, source_address, destination_address, sequence_number,
                 is_ack=False, data=None):
        self.source_address = source_address
        self.destination_address = destination_address
        self.sequence_number = sequence_number
        self.is_ack = is_ack
        self.data = data

    def __repr__(self):
        return ("Packet(Source IP: " + str(self.source_address) + 
                ", Dest IP: " + str(self.destination_address) +
                ", #Seq: " + str(self.sequence_number) + 
                ", Is ACK: " + str(self.is_ack) + 
                ", Data: " + str(self.data) + ")")

    def get_source_address(self):
        return self.source_address

    def get_destination_address(self):
        return self.destination_address

    def get_sequence_number(self):
        return self.sequence_number

    def set_sequence_number(self, seq_num):
        self.sequence_number = seq_num

    def get_is_ack(self):
        return self.is_ack

    def get_data(self):
        return self.data


class Communicator:
    def __init__(self, address):
        self.address = address
        self.current_seq_num = None

    def get_address(self):
        return self.address

    def get_current_sequence_number(self):
        return self.current_seq_num

    def set_current_sequence_number(self, seq_num):
        self.current_seq_num = seq_num

    def send_packet(self, packet):
        print("Sender: Packet Seq Num:", self.current_seq_num, "was sent")
        return packet

    def increment_current_seq_num(self):
        self.current_seq_num += 1


class Sender(Communicator):
    def __init__(self, address, num_letters_in_packet):
        super().__init__(address)
        self.num_letters_in_packet = num_letters_in_packet

    def is_special_string(self, message):
        # Iterate through each character in the input string
        for char in message:
            # If the character is not in the set of special characters, return False
            if char.isalpha():
                return False
        # If all characters are special, return True
        return True

    def prepare_packets(self, message, destination_address):
        packets = []
        counter = 0
        if len(message) > 0:
            for i in range(0, len(message), self.num_letters_in_packet):
                p_data = message[i:i + self.num_letters_in_packet]
                packet = Packet(self.address, destination_address, counter, is_ack=False, data=p_data)
                counter += 1
                packets.append(packet)
        else:
            packet = Packet(self.address, destination_address, 0, is_ack=False, data="")
            packets.append(packet)

        if self.is_special_string(message):
            return "Message contains only special characters"
        else:
            return packets

    def receive_ack(self, acknowledgment_packet):
        return acknowledgment_packet.get_is_ack()


class Receiver(Communicator):
    def __init__(self, address):
        super().__init__(address)
        self.received_packets = []

    def receive_packet(self, packet):
        self.received_packets.append(packet)
        print("Receiver: Received packet seq num:", packet.get_sequence_number())
        acknowledgement = Packet(packet.get_destination_address(), packet.get_source_address(),
                                 packet.get_sequence_number(), is_ack=True, data=None)
        return acknowledgement

    def get_message_by_received_packets(self):
        message = []
        for p in self.received_packets:
            message.append(p.get_data())
        return ''.join(message)


if __name__ == '__main__':
    source_address = "192.168.1.1"
    destination_address = "192.168.2.2"
    message = "!!!!!"
    num_letters_in_packet = 5

    sender = Sender(source_address, num_letters_in_packet)
    receiver = Receiver(destination_address)

    packets = sender.prepare_packets(message, receiver.get_address())

    if isinstance(packets, str):
        print(packets)
    else:
        # setting current packet
        start_interval_index = packets[0].get_sequence_number()
        # setting current packet in the sender and receiver
        sender.set_current_sequence_number(start_interval_index)
        receiver.set_current_sequence_number(start_interval_index)

        # setting the last packet
        last_packet_sequence_num = packets[-1].get_sequence_number()
        receiver_current_packet = receiver.get_current_sequence_number()

        while receiver_current_packet <= last_packet_sequence_num:
            current_index = sender.get_current_sequence_number()
            packet = packets[current_index]
            packet = sender.send_packet(packet)

            ack = receiver.receive_packet(packet)

            result = sender.receive_ack(ack)

            if result:
                sender.increment_current_seq_num()
                receiver.increment_current_seq_num()

            receiver_current_packet = receiver.get_current_sequence_number()

        full_message = receiver.get_message_by_received_packets()
        print(f"Receiver message: {full_message}")
