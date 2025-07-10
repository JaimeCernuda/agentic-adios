
# Gemini Agent for ADIOS MCP Server

This document provides a guide for using the ADIOS MCP server with a Gemini agent. The server exposes several tools to interact with ADIOS BP5 files.

## Capabilities

The ADIOS MCP server provides the following tools:

- **`list_bp5(directory: str) -> list[str]`**: Lists all `.bp` and `.bp5` files in a specified directory.
- **`inspect_variables(filename: str, variable_name: str = None) -> dict`**: Inspects variables in a BP5 file. If `variable_name` is provided, it returns information for that specific variable; otherwise, it returns information for all variables.
- **`inspect_variables_at_step(filename: str, variable_name: str, step: int) -> dict`**: Inspects a specific variable at a given step in a BP5 file.
- **`inspect_attributes(filename: str, variable_name: str = None) -> dict`**: Reads global or variable-specific attributes from a BP5 file.
- **`read_variable_at_step(filename: str, variable_name: str, target_step: int)`**: Reads a named variable at a specific step from a BP5 file.

## Usage

To use the ADIOS MCP server, you need to call the appropriate tool with the required parameters. Make sure to use **absolute paths** for all file and directory parameters.

### Example 1: List all BP5 files in a directory

To list all BP5 files in the `/home/gemini/workspace` directory, you would use the following command:

```
list_bp5(directory="/home/gemini/workspace)
```

### Example 2: Inspect all variables in a BP5 file

To inspect all variables in the `Lammps-melting-gold.bp5` file located in the `/home/gemini/workspace` directory, you would use the following command:

```
inspect_variables(filename="/home/gemini/workspace/Lammps-melting-gold.bp5")
```

### Example 3: Inspect a specific variable in a BP5 file

To inspect the `atoms` variable in the `Lammps-melting-gold.bp5` file, you would use the following command:

```
inspect_variables(filename="/home/gemini/workspace/Lammps-melting-gold.bp5", variable_name="atoms")
```

### Example 4: Inspect a variable at a specific step

To inspect the `atoms` variable at step `5` in the `Lammps-melting-gold.bp5` file, you would use the following command:

```
inspect_variables_at_step(filename="/home/gemini/workspace/Lammps-melting-gold.bp5", variable_name="atoms", step=5)
```

### Example 5: Inspect global attributes

To inspect the global attributes of the `Lammps-melting-gold.bp5` file, you would use the following command:

```
inspect_attributes(filename="/home/gemini/workspace/Lammps-melting-gold.bp5")
```

### Example 6: Inspect attributes of a specific variable

To inspect the attributes of the `atoms` variable in the `Lammps-melting-gold.bp5` file, you would use the following command:

```
inspect_attributes(filename="/home/gemini/workspace/Lammps-melting-gold.bp5", variable_name="atoms")
```

### Example 7: Read a variable at a specific step

To read the value of the `atoms` variable at step `10` in the `Lammps-melting-gold.bp5` file, you would use the following command:

```
read_variable_at_step(filename="/home/gemini/workspace/Lammps-melting-gold.bp5", variable_name="atoms", target_step=10)
```
