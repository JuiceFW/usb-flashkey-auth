import wmi

c = wmi.WMI()

for disk in c.Win32_DiskDrive(InterfaceType="USB"):
    print("=" * 40)
    print("Model:", disk.Model)
    print("Caption:", disk.Caption)
    print("Name:", disk.Name)
    print("DeviceID:", disk.DeviceID)
    print("PNPDeviceID:", disk.PNPDeviceID)
    print("SerialNumber:", disk.SerialNumber)

    for part in disk.associators("Win32_DiskDriveToDiskPartition"):
        for log in part.associators("Win32_LogicalDiskToPartition"):
            print(" Drive:", log.DeviceID)
            print(" VolumeName:", log.VolumeName)
            print(" VolumeSerial:", log.VolumeSerialNumber)
