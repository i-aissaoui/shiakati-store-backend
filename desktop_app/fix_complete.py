#!/usr/bin/env python3

file_path = 'src/utils/api_client.py'

# Read the file content
with open(file_path, 'r') as f:
    content = f.read()

# Define the problematic section
bad_code = """                variants = response.json()
                if not variants:
                    print("No variants found in inventory")
                    return []
                except requests.Timeout:
                    print("Timeout while getting product data - server taking too long to respond")
                    return []
            except requests.ConnectionError:                return []
            except Exception as e:
                return []"""

# Define the fixed code
good_code = """                variants = response.json()
                if not variants:
                    print("No variants found in inventory")
                    return []
                print(f"Retrieved {len(variants)} variants")

            except requests.Timeout:
                print("Timeout while getting variants - server taking too long to respond")
                return []
            except requests.ConnectionError:
                print("Connection error - check if the server is running")
                return []
            except Exception as e:
                print(f"Unexpected error getting variants: {str(e)}")
                return []"""

# Replace the bad code with the good code
fixed_content = content.replace(bad_code, good_code)

# Write the fixed content back to the file
with open(file_path, 'w') as f:
    f.write(fixed_content)

print(f"Fixed the syntax error in {file_path}")
