from queue import Queue
from threading import Thread
import move
from move import Move_Command

# A thread that produces data
def ui(out_q):
    while True:
        print("Input values  [i] or exit [e]")
        user_choice = input()
        if user_choice == 'i':
            # new input values
            mc = Move_Command()
            
            print("Please enter the values")
            print("Speed:")
            mc.set_speed(int(input()))
            print("direction:")
            mc.set_direction(input())
            print("turn:")
            mc.set_turn(input())
            print("radius:")
            mc.set_radius(float(input()))
            out_q.put(mc)
            
        elif user_choice == 'e':
            print("bye")
            mc = Move_Command()
            mc.set_stop_working(True)
            out_q.put(mc)
            break
        # else: do nothing
          
# Create the shared queue and launch both threads
working_queue = Queue()
t_mh = Thread(target = move.move_handler, args =(working_queue, ))
t_ui = Thread(target = ui, args =(working_queue, ))
t_mh.start()
t_ui.start()
  
# Wait for all produced items to be consumed
working_queue.join()