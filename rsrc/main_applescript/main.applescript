-- Get the current working directory. If the app is double-clicked, cwd is in Blade Runner.app. If the AppleScript is run directly, then the cwd is the path to the main.scpt.
set currentPath to (path to me) as Unicode text

-- Determine if app or applescript was run and find Blade Runner's root directory inside Resources. 
if currentPath contains "main.scpt" then
	tell application "Finder"
		set scriptsDir to get container of (path to me)
		set resourcesDir to get container of scriptsDir
		set appRootDir to ((resourcesDir as Unicode text) & "Blade Runner")
	end tell
else
	tell application "Finder"
		set scriptsDir to get container of (path to me)
		set resourcesDir to get container of scriptsDir
		set appRootDir to (path to me as Unicode text) & "Contents:Resources:Blade Runner"
	end tell
end if

-- Convert the root directory to POSIX path.
set appRootDir to quoted form of (POSIX path of appRootDir)

-- Start Blade Runner.
do shell script "cd " & appRootDir & "; /usr/bin/python -m blade_runner.runner > /dev/null 2>&1 &" with administrator privileges
