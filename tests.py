components = {
    3: 'Z',
    1: 'X',
    -1: 'Y'
}

# Loop over the dictionary in ascending order of keys
for key in sorted(components):
    component = components[key]
    print(f"Key: {key}, Component: {component}")