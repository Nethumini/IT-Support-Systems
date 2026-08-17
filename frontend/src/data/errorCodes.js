/**
 * Common Error Codes Database
 * Contains error codes for Windows, Mac, and Linux systems
 * Each entry includes: code, description, potential reason, and mitigation steps
 */

export const errorCodes = {
  windows: [
    {
      code: '0x0000007E',
      name: 'SYSTEM_THREAD_EXCEPTION_NOT_HANDLED',
      description: 'A system thread generated an exception that the error handler did not catch.',
      potentialReason: 'Corrupted system files, incompatible drivers, or hardware issues',
      mitigationSteps: [
        'Run System File Checker: sfc /scannow',
        'Update device drivers, especially graphics and network drivers',
        'Check Windows Event Viewer for specific driver errors',
        'Run Windows Memory Diagnostic tool',
        'Perform a clean boot to identify conflicting software',
        'Update Windows to the latest version'
      ],
      severity: 'high'
    },
    {
      code: '0x00000050',
      name: 'PAGE_FAULT_IN_NONPAGED_AREA',
      description: 'Invalid system memory has been referenced',
      potentialReason: 'Faulty RAM, corrupted system files, or incompatible software',
      mitigationSteps: [
        'Run Windows Memory Diagnostic: mdsched.exe',
        'Check RAM modules - reseat or replace if faulty',
        'Run System File Checker: sfc /scannow',
        'Update or remove recently installed software',
        'Check disk for errors: chkdsk /f /r',
        'Update device drivers'
      ],
      severity: 'critical'
    },
    {
      code: '0x0000007B',
      name: 'INACCESSIBLE_BOOT_DEVICE',
      description: 'Windows cannot access the system partition or boot volume',
      potentialReason: 'Corrupted boot files, disk errors, or incorrect BIOS settings',
      mitigationSteps: [
        'Run Startup Repair from Windows Recovery Environment',
        'Rebuild BCD: bootrec /rebuildbcd',
        'Check disk for errors: chkdsk /f /r',
        'Verify BIOS settings - ensure AHCI/IDE mode is correct',
        'Check SATA/HDD cables and connections',
        'Run System File Checker: sfc /scannow'
      ],
      severity: 'critical'
    },
    {
      code: '0x0000000A',
      name: 'IRQL_NOT_LESS_OR_EQUAL',
      description: 'A kernel-mode process or driver attempted to access memory at an invalid address',
      potentialReason: 'Faulty drivers, corrupted system files, or hardware incompatibility',
      mitigationSteps: [
        'Update all device drivers, especially graphics and network',
        'Run System File Checker: sfc /scannow',
        'Check Windows Event Viewer for driver errors',
        'Perform clean boot to identify problematic software',
        'Update Windows to latest version',
        'Check for hardware compatibility issues'
      ],
      severity: 'high'
    },
    {
      code: '0x80070005',
      name: 'Access Denied',
      description: 'Permission denied error when accessing files or folders',
      potentialReason: 'Insufficient permissions, corrupted user profile, or UAC restrictions',
      mitigationSteps: [
        'Run application as Administrator',
        'Check file/folder permissions - right-click > Properties > Security',
        'Take ownership of the file/folder',
        'Disable UAC temporarily (not recommended for long-term)',
        'Check if antivirus is blocking access',
        'Repair user profile if corrupted'
      ],
      severity: 'medium'
    },
    {
      code: '0x80070002',
      name: 'File Not Found',
      description: 'Windows cannot find the specified file',
      potentialReason: 'Missing system files, corrupted installation, or incorrect path',
      mitigationSteps: [
        'Run System File Checker: sfc /scannow',
        'Run DISM: DISM /Online /Cleanup-Image /RestoreHealth',
        'Verify file path is correct',
        'Check if file was deleted or moved',
        'Restore from backup if available',
        'Reinstall the application causing the error'
      ],
      severity: 'medium'
    },
    {
      code: '0x80070003',
      name: 'Path Not Found',
      description: 'The system cannot find the path specified',
      potentialReason: 'Invalid path, network drive disconnected, or missing directory',
      mitigationSteps: [
        'Verify the path is correct and exists',
        'Check if network drive is mapped correctly',
        'Recreate missing directories',
        'Check for typos in the path',
        'Ensure drive letter is correct',
        'Check disk space availability'
      ],
      severity: 'low'
    },
    {
      code: '0x80070020',
      name: 'Sharing Violation',
      description: 'The process cannot access the file because it is being used by another process',
      potentialReason: 'File is locked by another application or process',
      mitigationSteps: [
        'Close the application using the file',
        'End the process in Task Manager',
        'Restart the application',
        'Check for background processes accessing the file',
        'Use Process Explorer to find locking process',
        'Restart computer if file remains locked'
      ],
      severity: 'low'
    },
    {
      code: '0xC000021A',
      name: 'Fatal System Error',
      description: 'A fatal system error has occurred. The system has been shut down',
      potentialReason: 'Corrupted system files, incompatible drivers, or registry corruption',
      mitigationSteps: [
        'Boot into Safe Mode',
        'Run System File Checker: sfc /scannow',
        'Run DISM: DISM /Online /Cleanup-Image /RestoreHealth',
        'Restore system to previous restore point',
        'Check Windows Event Viewer for specific errors',
        'Update or rollback recent driver updates'
      ],
      severity: 'critical'
    },
    {
      code: '0x80070057',
      name: 'Invalid Parameter',
      description: 'The parameter is incorrect',
      potentialReason: 'Invalid input, corrupted registry, or application bug',
      mitigationSteps: [
        'Verify input parameters are correct',
        'Clear application cache and temp files',
        'Repair registry using System File Checker',
        'Update the application',
        'Reinstall the application',
        'Check application logs for specific parameter errors'
      ],
      severity: 'medium'
    }
  ],
  mac: [
    {
      code: 'Kernel Panic',
      name: 'Kernel Panic',
      description: 'macOS kernel encountered an unrecoverable error and halted the system',
      potentialReason: 'Hardware failure, corrupted system files, incompatible kernel extensions, or faulty RAM',
      mitigationSteps: [
        'Restart Mac and check if issue persists',
        'Boot into Safe Mode (hold Shift during startup)',
        'Reset NVRAM/PRAM: Restart and hold Option+Command+P+R',
        'Run Apple Diagnostics: Hold D during startup',
        'Check Console.app for specific error messages',
        'Remove recently installed kernel extensions',
        'Update macOS to latest version',
        'Check RAM using Apple Diagnostics'
      ],
      severity: 'critical'
    },
    {
      code: '-36',
      name: 'ioErr',
      description: 'I/O error - cannot read or write to disk',
      potentialReason: 'Disk corruption, failing hard drive, or file system errors',
      mitigationSteps: [
        'Run First Aid in Disk Utility',
        'Check disk health: diskutil verifyVolume /',
        'Repair disk permissions: diskutil repairPermissions /',
        'Backup important data immediately',
        'Run fsck in Recovery Mode if needed',
        'Check S.M.A.R.T. status of drive',
        'Consider replacing failing drive'
      ],
      severity: 'high'
    },
    {
      code: '-50',
      name: 'paramErr',
      description: 'Parameter error - invalid parameter passed to function',
      potentialReason: 'Application bug, corrupted preferences, or invalid input',
      mitigationSteps: [
        'Update the application to latest version',
        'Delete application preferences: ~/Library/Preferences/',
        'Clear application cache',
        'Reinstall the application',
        'Check application logs in Console.app',
        'Verify input parameters are correct'
      ],
      severity: 'medium'
    },
    {
      code: '-108',
      name: 'resNotFound',
      description: 'Resource not found - required resource is missing',
      potentialReason: 'Missing application resources, corrupted installation, or deleted files',
      mitigationSteps: [
        'Reinstall the application',
        'Check if application files are complete',
        'Verify application is not corrupted',
        'Download fresh copy from App Store or developer',
        'Clear application cache',
        'Check disk for errors'
      ],
      severity: 'medium'
    },
    {
      code: '-43',
      name: 'fnfErr',
      description: 'File not found',
      potentialReason: 'File was moved, deleted, or path is incorrect',
      mitigationSteps: [
        'Verify file path is correct',
        'Search for file using Spotlight',
        'Check Trash for deleted file',
        'Restore from Time Machine backup',
        'Verify file permissions',
        'Check if file exists in expected location'
      ],
      severity: 'low'
    },
    {
      code: '-61',
      name: 'eofErr',
      description: 'End of file error',
      potentialReason: 'Unexpected end of file, corrupted file, or incomplete download',
      mitigationSteps: [
        'Re-download the file',
        'Check file integrity',
        'Verify file is not corrupted',
        'Check disk space availability',
        'Check network connection if downloading',
        'Try opening file with different application'
      ],
      severity: 'low'
    },
    {
      code: '-1401',
      name: 'userCanceledErr',
      description: 'User canceled the operation',
      potentialReason: 'User intentionally canceled, or system timeout',
      mitigationSteps: [
        'Retry the operation',
        'Check if operation timed out',
        'Increase timeout settings if applicable',
        'Check system resources',
        'Close other applications to free resources',
        'Restart the application'
      ],
      severity: 'low'
    },
    {
      code: 'dyld: Library not loaded',
      name: 'Dynamic Library Error',
      description: 'Dynamic linker cannot find required library',
      potentialReason: 'Missing library files, incompatible library version, or corrupted installation',
      mitigationSteps: [
        'Reinstall the application',
        'Update macOS to latest version',
        'Install missing dependencies',
        'Check library paths: echo $DYLD_LIBRARY_PATH',
        'Verify library exists: ls -la /usr/lib/',
        'Run: sudo update_dyld_shared_cache'
      ],
      severity: 'medium'
    },
    {
      code: 'com.apple.xpc.launchd[1]',
      name: 'Launch Daemon Error',
      description: 'Launch daemon cannot start or manage service',
      potentialReason: 'Corrupted plist file, permission issues, or service conflict',
      mitigationSteps: [
        'Check Console.app for specific error',
        'Verify plist file: /Library/LaunchDaemons/',
        'Fix permissions: sudo chmod 644 plist_file',
        'Unload and reload service: launchctl unload/load',
        'Remove corrupted plist and reinstall',
        'Check disk for errors'
      ],
      severity: 'medium'
    },
    {
      code: 'disk0s2: I/O error',
      name: 'Disk I/O Error',
      description: 'Cannot read or write to disk',
      potentialReason: 'Failing hard drive, disk corruption, or connection issues',
      mitigationSteps: [
        'Run First Aid in Disk Utility immediately',
        'Backup all important data',
        'Check S.M.A.R.T. status',
        'Verify disk connections',
        'Run fsck in Recovery Mode',
        'Consider replacing failing drive',
        'Check Console.app for specific errors'
      ],
      severity: 'critical'
    }
  ],
  linux: [
    {
      code: 'Kernel Oops',
      name: 'Kernel Oops',
      description: 'Linux kernel encountered a non-fatal error',
      potentialReason: 'Hardware issues, driver bugs, or kernel bugs',
      mitigationSteps: [
        'Check kernel logs: dmesg | tail -50',
        'Check system logs: journalctl -k',
        'Update kernel and drivers',
        'Check hardware compatibility',
        'Review kernel oops details in /var/log/',
        'Report bug to kernel developers if reproducible',
        'Try different kernel version'
      ],
      severity: 'high'
    },
    {
      code: 'Kernel Panic',
      name: 'Kernel Panic',
      description: 'Linux kernel encountered fatal error and halted system',
      potentialReason: 'Hardware failure, corrupted filesystem, or critical kernel bug',
      mitigationSteps: [
        'Check hardware (RAM, disk, CPU)',
        'Boot from recovery/rescue mode',
        'Check filesystem: fsck -f /dev/sda1',
        'Review kernel logs before panic',
        'Update kernel if bug is known',
        'Check for hardware overheating',
        'Verify disk integrity'
      ],
      severity: 'critical'
    },
    {
      code: 'ENOENT (2)',
      name: 'No such file or directory',
      description: 'File or directory does not exist',
      potentialReason: 'File was deleted, moved, or path is incorrect',
      mitigationSteps: [
        'Verify file path is correct',
        'Check if file exists: ls -la /path/to/file',
        'Search for file: find / -name filename',
        'Restore from backup if deleted',
        'Check file permissions',
        'Verify mount points are correct'
      ],
      severity: 'low'
    },
    {
      code: 'EACCES (13)',
      name: 'Permission denied',
      description: 'Access denied due to insufficient permissions',
      potentialReason: 'Insufficient file permissions or user privileges',
      mitigationSteps: [
        'Check file permissions: ls -l filename',
        'Change permissions: chmod 755 filename',
        'Change ownership: chown user:group filename',
        'Use sudo if root access needed',
        'Check SELinux/AppArmor policies',
        'Verify user is in correct group'
      ],
      severity: 'medium'
    },
    {
      code: 'ENOSPC (28)',
      name: 'No space left on device',
      description: 'Disk is full or inode limit reached',
      potentialReason: 'Disk full, too many small files, or inode exhaustion',
      mitigationSteps: [
        'Check disk usage: df -h',
        'Check inode usage: df -i',
        'Free up disk space',
        'Remove old logs: journalctl --vacuum-time=7d',
        'Find large files: du -sh /* | sort -h',
        'Clean package cache: apt/yum clean',
        'Remove unused packages'
      ],
      severity: 'high'
    },
    {
      code: 'EIO (5)',
      name: 'Input/output error',
      description: 'Hardware I/O error',
      potentialReason: 'Failing disk, bad sectors, or hardware connection issues',
      mitigationSteps: [
        'Check disk health: smartctl -a /dev/sda',
        'Check disk errors: dmesg | grep -i error',
        'Run filesystem check: fsck -f /dev/sda1',
        'Backup data immediately',
        'Check disk connections',
        'Replace failing hardware',
        'Check S.M.A.R.T. status'
      ],
      severity: 'critical'
    },
    {
      code: 'ENOMEM (12)',
      name: 'Out of memory',
      description: 'System ran out of available memory',
      potentialReason: 'Memory leak, insufficient RAM, or too many processes',
      mitigationSteps: [
        'Check memory usage: free -h',
        'Identify memory-hungry processes: top or htop',
        'Kill unnecessary processes',
        'Add swap space if needed',
        'Check for memory leaks',
        'Restart services consuming memory',
        'Consider adding more RAM'
      ],
      severity: 'high'
    },
    {
      code: 'ECONNREFUSED (111)',
      name: 'Connection refused',
      description: 'Connection to service was refused',
      potentialReason: 'Service not running, firewall blocking, or wrong port',
      mitigationSteps: [
        'Check if service is running: systemctl status service_name',
        'Start the service: systemctl start service_name',
        'Check firewall rules: iptables -L or firewall-cmd --list-all',
        'Verify service is listening: netstat -tulpn | grep port',
        'Check service logs: journalctl -u service_name',
        'Verify port number is correct'
      ],
      severity: 'medium'
    },
    {
      code: 'ETIMEDOUT (110)',
      name: 'Connection timed out',
      description: 'Connection attempt timed out',
      potentialReason: 'Network issues, firewall blocking, or service not responding',
      mitigationSteps: [
        'Check network connectivity: ping hostname',
        'Verify service is running and accessible',
        'Check firewall rules',
        'Increase timeout settings',
        'Check DNS resolution: nslookup hostname',
        'Verify network routes: ip route',
        'Check service logs for errors'
      ],
      severity: 'medium'
    },
    {
      code: 'SIGSEGV (11)',
      name: 'Segmentation fault',
      description: 'Application accessed invalid memory address',
      potentialReason: 'Application bug, memory corruption, or incompatible library',
      mitigationSteps: [
        'Update application to latest version',
        'Check application logs',
        'Run with debugger: gdb application',
        'Check for memory leaks: valgrind',
        'Verify library compatibility',
        'Report bug to application developers',
        'Try different application version'
      ],
      severity: 'high'
    }
  ]
}

/**
 * Search error codes across all platforms
 */
export const searchErrorCodes = (query, platform = null) => {
  const platforms = platform ? [platform] : ['windows', 'mac', 'linux']
  const results = []
  
  platforms.forEach(plat => {
    if (errorCodes[plat]) {
      errorCodes[plat].forEach(error => {
        const searchText = `${error.code} ${error.name} ${error.description} ${error.potentialReason}`.toLowerCase()
        if (searchText.includes(query.toLowerCase())) {
          results.push({ ...error, platform: plat })
        }
      })
    }
  })
  
  return results
}

/**
 * Get error code by code and platform
 */
export const getErrorByCode = (code, platform) => {
  if (errorCodes[platform]) {
    return errorCodes[platform].find(error => 
      error.code.toLowerCase() === code.toLowerCase()
    )
  }
  return null
}

