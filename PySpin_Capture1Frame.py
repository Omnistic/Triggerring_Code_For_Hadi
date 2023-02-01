import matplotlib.pyplot as plt
import numpy as np
import PySpin


class Camera:
    def __init__(self):
        # Timeout value [ms]
        self.__timeout = 1000
        
        # Retrieve singleton reference to system object
        self.__system = PySpin.System.GetInstance()
        
        # Retrieve list of cameras from the system
        self.__cam_list = self.__system.GetCameras()
        
        # Number of cameras
        num_cams = self.__cam_list.GetSize()
        
        # Check if at least one camera is available
        if not num_cams:
            print('ERROR: Camera not found...')
            del self
        
        # Get first camera only
        self.__camera = self.__cam_list[0]
        
        # Initialize camera
        self.__camera.Init()
        
        # Retrieve GenICam nodemap
        self.__nodemap = self.__camera.GetNodeMap()
        
    def CaptureOneFrame(self):
        # Set acquisition mode to: Single frame
        node_acq_mode = self.__nodemap.GetNode('AcquisitionMode')
        node_acq_mode = PySpin.CEnumerationPtr(node_acq_mode)
        node_acq_mode_single = node_acq_mode.GetEntryByName('SingleFrame')
        node_acq_mode_single = node_acq_mode_single.GetValue()
        node_acq_mode.SetIntValue(node_acq_mode_single)
        
        # Begin image acquisition
        self.__camera.BeginAcquisition()

        # Frame completion flag
        frame_incomplete = True
        
        # Loop until a frame is grabbed
        while frame_incomplete:
            # Try grabbing one frame
            frame = self.__camera.GetNextImage(self.__timeout)
        
            # Continue looping until the frame is complete
            frame_incomplete = frame.IsIncomplete()
        
        # Retrieve frame data
        frame_data = frame.GetNDArray()
        
        # Release the frame
        frame.Release()
           
        # Stop image acquisition
        self.__camera.EndAcquisition()
        
        return frame_data
        
    def SetExposure(self, exp_time):
        # Disables continous exposure mode
        self.__camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        
        # Maximum exposure time (seems to be 13181 ms for GS3-U3-51S5M-C)
        max_exp_time = self.__camera.ExposureTime.GetMax()
        
        # Makes exposure time valid
        exp_time = min(max_exp_time, exp_time)
        
        # Set exposure time
        self.__camera.ExposureTime.SetValue(exp_time)
        
    def SetGain(self, gain):
        # Disables continuous gain mode
        self.__camera.GainAuto.SetValue(PySpin.GainAuto_Off)
        
        # Maximum gain (seems to be 47 for GS3-U3-51S5M-C)
        max_gain = self.__camera.Gain.GetMax()
        
        # Makes gain valid
        gain = min(max_gain, gain)
        
        # Set gain
        self.__camera.Gain.SetValue(gain)
    
    def ResetExposure(self):
        # Set exposure to continuous without error trapping
        self.__camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
    
    def ResetGain(self):
        # Set gain to continuous without error trapping
        self.__camera.GainAuto.SetValue(PySpin.GainAuto_Continuous)
    
    def __del__(self):
        # Deinitialize camera
        self.__camera.DeInit()
        
        # Clear camera list before releasing system
        self.__cam_list.Clear()
        
        # Release system instance
        self.__system.ReleaseInstance()


def main():
    # Connect camera
    cam = Camera()
    
    # Set exposure time and gain
    cam.SetExposure(1000)
    cam.SetGain(1)
    
    # Display one frame
    plt.imshow(np.array(cam.CaptureOneFrame()))
    plt.colorbar()
    
    # Reset exposure and gain
    cam.ResetExposure()
    cam.ResetGain()
    
    # Release camera
    del cam
    
    return True

    
if __name__ == '__main__':
    main()