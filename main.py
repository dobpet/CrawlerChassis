from Model import GlobalVars
import sys
import utime
import uasyncio
import gc
from machine import freq


        
GV = None
RunRequest = True

def btnESC_ShortPressed():
    print(' --> btnESC shortly pressed')
    
def btnENT_ShortPressed():
    print(' --> btnENT shortly pressed')
    
def btnESC_LongPressed():
    global RunRequest
    RunRequest = False

print("=========  RPW APPLICATION STARTED  =========")
async def main():
    global GV, RunRequest
    gc.threshold((gc.mem_free() + gc.mem_alloc()) // 4)
    freq(240000000)
    GV = GlobalVars()
    GV.Board.btnESC_ShortPress(btnESC_ShortPressed)
    GV.Board.btnENT_ShortPress(btnENT_ShortPressed)
    GV.Board.btnESC_LongPress(btnESC_LongPressed)
    ts = utime.time()    
    while RunRequest:
        if (utime.time()-ts) > 20:
            RunRequest = True

        await uasyncio.sleep_ms(1)
    print(' -> GUI shutdown requested')

async def shutdown():
    global GV
    if GV != None:
        GV.deinit()
        GV = None
        gc.collect()
    freq(100000000)


if __name__ == '__main__':
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        print(' -> REPL interrupt requested')
    except Exception as e:
        import sys
        print()
        print('====================ERROR====================') 
        sys.print_exception(e)
        print('---------------------------------------------')
        print()
    finally:
        uasyncio.run(shutdown())
        print("=========  RPW APPLICATION STOPPED  =========")