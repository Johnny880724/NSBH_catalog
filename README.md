# NSBH_catalog setup

This guide will walk you through setting up the project and preparing Maya for use. Follow the steps below carefully.

## 1. Clone or Pull Latest Changes from the GitHub Repository

1. **Clone the repository** (if you haven't already) or pull the latest changes if you have already cloned the repository:
   ```bash
   git pull origin main
   ```
   If you haven’t cloned the repo, you can do it by running:
   ```bash
   git clone <repository_url>
   ```

## 2. Setting Up the Project Directory

1. Create a new project directory (or use the `Maya_tutorial` directory from the tutorial).
   ```bash
   mkdir -p ~/your_project_directory
   ```

2. Inside the project directory, create a new directory called `tools/`:
   ```bash
   mkdir tools
   ```

3. Move the `PNevo.tar.gz` file into the `tools/` directory.

4. Decompress the `PNevo.tar.gz` file:
   ```bash
   tar -xzvf tools/PNevo.tar.gz
   ```

## 3. Prepare the `PNevo` Directory

1. Navigate to the `tools/PNevo` directory:
   ```bash
   cd tools/PNevo
   ```

2. Move the `initdata_NSBH.mpar` file into this directory (there should already be a `test.mpar` file here):
   ```bash
   mv initdata_NSBH.mpar tools/PNevo/
   ```

3. Ensure that the `test.mpar` file is already present in the `tools/PNevo/` directory.

4. Run the following command to compile:
   ```bash
   make
   ```

---

## 4. Preparing Maya

1. **Install Cactus** if it hasn’t been done already in your project directory.

2. Move the `BHNSThorns.tar.gz` file into the `/Cactus/repos/` directory and decompress:
   ```bash
   mv BHNSThorns.tar.gz /Cactus/repos/
   tar -xzvf /Cactus/repos/BHNSThorns.tar.gz
   ```

3. Navigate to the `/Cactus/arrangements/` directory and create a symbolic link for the `BHNSThorns` repository:
   ```bash
   cd /Cactus/arrangements/
   ln -s ../repos/BHNSThorns/ .
   ```

4. Move the [bhns_maya.th](http://bhns_maya.th/) file into the `/Cactus/thornlists` directory:
   ```bash
   mv bhns_maya.th /Cactus/thornlists/
   ```

5. Return to the `/Cactus` directory and compile the Cactus code:
   ```bash
   cd /Cactus
   ./simfactory/bin/sim build bhns_Maya --thornlist ./thornlists/bhns_maya.th --machine uxmal
   ```

---

### Notes:
- Ensure you have all the necessary permissions to create directories and move files.
- Follow the steps in order to avoid missing dependencies or configuration issues.
- If any errors occur during the process, please check the log for additional details or reach out for further assistance.
