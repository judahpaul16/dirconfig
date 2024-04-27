package main

import (
	"fmt"
	"os/exec"
)

func main() {
	newPathEntry := `C:\Program Files\UrBackup\`

	// Check if newPathEntry is already in the PATH and add if not present
	cmd := exec.Command("powershell", "-Command",
		`$newPathEntry = '`+newPathEntry+`';
		$envPath = [Environment]::GetEnvironmentVariable("PATH", "User");
		if ($envPath -split ";" -contains $newPathEntry) {
			Write-Output "Already in PATH"
		} else {
			$newPath = $envPath + ";" + $newPathEntry;
			[Environment]::SetEnvironmentVariable("PATH", $newPath, "User");
			Write-Output "Added to PATH"
		}`)

	// Execute the command
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Printf("Failed to modify the system PATH: %s\n", err)
		return
	}

	fmt.Printf("Output: %s\n", string(output))
}
