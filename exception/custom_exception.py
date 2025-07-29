import traceback
import sys
from logger.custom_logger import CustomLogger
logger=CustomLogger().get_logger(__file__)

class DocumentPortalException(Exception):
    """Custom exception for Document Portal"""
    def __init__(self,error_message):
        _,_,exc_tb= sys.exc_info()
        # If exc_tb is None (no active exception), get the current frame info
        if exc_tb is None:
            current_frame = sys._getframe(1)  # Get the caller's frame
            self.file_name = current_frame.f_code.co_filename
            self.lineno = current_frame.f_lineno
            self.traceback_str = f"Exception raised at {self.file_name}:{self.lineno}"
        else:
            self.file_name = exc_tb.tb_frame.f_code.co_filename
            self.lineno = exc_tb.tb_lineno
            self.traceback_str = ''.join(traceback.format_exception(*sys.exc_info()))
            
        self.error_message = str(error_message) 
        
    def __str__(self):
       return f"""
        Error in [{self.file_name}] at line [{self.lineno}]
        Message: {self.error_message}
        Traceback:
        {self.traceback_str}
        """
    
if __name__ == "__main__":
    try:
        # Simulate an error
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exc=DocumentPortalException(e)
        logger.error(app_exc)
        raise app_exc