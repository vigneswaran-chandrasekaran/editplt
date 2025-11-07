import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

def plt2json(axs, json_file_path, pprint=False):
    """
    Extracts plot data and metadata into a serializable dictionary.
    """

    if hasattr(axs, 'shape'):
        if len(axs.shape) == 1:
            if axs.shape[0] == 1:
                m = 1
                n = axs.shape[-1]
            else:
                m = axs.shape[0]
                n = 1
        else:
            m, n = axs.shape
    else:
        m, n = 1, 1

    subplots_dict = []

    for row in range(m):
        for col in range(n):
            
            if m == 1 and n == 1:
                ax = axs
            elif len(axs.shape) == 1:
                ax = axs[row] if axs.shape[0] > 1 else axs[col]
            else:
                ax = axs[row, col]

            plot_dict = {
                'lines': [],
                'collections': [],
                'patches': [],
                'images': [],
                'metadata': {},
                'subplot_index': (row, col)
            }

            # 1. Serialize Lines
            for line in ax.lines:
                x_data, y_data = line.get_data()
                plot_dict['lines'].append({
                    'x_data': list(x_data), # Convert numpy array to list for JSON
                    'y_data': list(y_data),
                    'label': line.get_label(),
                    'color': line.get_color(),
                    'linestyle': line.get_linestyle()
                })

            # 2. Serialize Collections (like scatter)
            for col in ax.collections:
                plot_dict['collections'].append({
                    'data_offsets': col.get_offsets().tolist(), # tolist() for JSON
                    'label': col.get_label(),
                    'facecolors': col.get_facecolors().tolist()
                })
                
            # 3. Serialize Patches (like bars)
            for patch in ax.patches:
                plot_dict['patches'].append({
                    'x': float(patch.get_x()),
                    'y': float(patch.get_y()),
                    'width': float(patch.get_width()),
                    'height': float(patch.get_height()),
                    'label': patch.get_label(),
                    'facecolor': patch.get_facecolor()
                })

            # 4. Serialize Metadata
            plot_dict['metadata'] = {
                'title': ax.get_title(),
                'xlabel': ax.get_xlabel(),
                'ylabel': ax.get_ylabel(),
                'xlim': ax.get_xlim(),
                'ylim': ax.get_ylim(),
            }
            
            # 5. Serialize Images (from imshow)
            for image in ax.images:
                norm = image.norm
                
                plot_dict['images'].append({
                    'data_array': image.get_array().tolist(), # Convert to list for JSON
                    'cmap': image.get_cmap().name,
                    'interpolation': image.get_interpolation(),
                    'vmin': norm.vmin,
                    'vmax': norm.vmax,
                    'extent': image.get_extent(),
                    'aspect': ax.get_aspect()
                })
            # Add legend info if it exists
            if ax.get_legend():
                plot_dict['metadata']['legend'] = [t.get_text() for t in ax.get_legend().get_texts()]
            if ax.get_title():
                plot_dict['metadata']['title'] = ax.get_title()

            subplots_dict.append(plot_dict)

    with open(json_file_path, 'w') as f:
        json.dump(subplots_dict, f, indent=2)

    if pprint:
        print(json.dumps(subplots_dict, indent=4, default=str)) # Use default=str to handle any tricky types

def json2plt(json_file_path):
    """
    Recreates a Matplotlib figure, including subplots,
    from a serialized JSON file.
    """
    
    # 1. Load the list of subplot dictionaries
    with open(json_file_path, 'r') as f:
        subplots_data = json.load(f)

    if not subplots_data:
        print("No data to plot.")
        return None, None

    # 2. Determine the grid shape (m, n) from the saved indices
    max_row = 0
    max_col = 0
    for plot_dict in subplots_data:
        row, col = plot_dict['subplot_index']
        max_row = max(max_row, row)
        max_col = max(max_col, col)
    
    m = max_row + 1
    n = max_col + 1

    # 3. Create the figure and axes grid
    # We add a sensible figsize. squeeze=False can simplify
    # indexing, but we'll handle it manually for clarity.
    fig, axs = plt.subplots(m, n, figsize=(5*n, 4*m))

    # 4. Iterate through each saved subplot's data and plot it
    for plot_dict in subplots_data:
        row, col = plot_dict['subplot_index']
        
        if m == 1 and n == 1:
            ax = axs
        elif m == 1: # 1D array, shape (n,)
            ax = axs[col]
        elif n == 1: # 1D array, shape (m,)
            ax = axs[row]
        else: # 2D array, shape (m, n)
            ax = axs[row, col]

        # 5. Re-plot lines
        for line_data in plot_dict.get('lines', []):
            ax.plot(
                line_data['x_data'],
                line_data['y_data'],
                label=line_data['label'],
                color=line_data['color'],
                linestyle=line_data['linestyle']
            )

        # 6. Re-plot collections (scatter)
        for col_data in plot_dict.get('collections', []):
            offsets = np.array(col_data['data_offsets'])
            ax.scatter(
                offsets[:, 0], # x data
                offsets[:, 1], # y data
                label=col_data['label'],
                facecolors=np.array(col_data['facecolors'])
            )
        
        # 7. Re-plot patches (bars)
        for patch_data in plot_dict.get('patches', []):
            rect = patches.Rectangle(
                (patch_data['x'], patch_data['y']),
                patch_data['width'],
                patch_data['height'],
                facecolor=patch_data['facecolor'],
                label=patch_data['label']
            )
            ax.add_patch(rect)
        
        # 8. Re-plot images (imshow)
        for image_data in plot_dict.get('images', []):
            im = ax.imshow(
                np.array(image_data['data_array']),
                cmap=image_data['cmap'],
                interpolation=image_data['interpolation'],
                vmin=image_data['vmin'],
                vmax=image_data['vmax'],
                extent=image_data['extent'],
                aspect=image_data['aspect']
            )
            # Add the colorbar back
            fig.colorbar(im, ax=ax)

        # 9. Re-apply metadata
        meta = plot_dict.get('metadata', {})
        if 'title' in meta:
            ax.set_title(meta['title'])
        if 'xlabel' in meta:
            ax.set_xlabel(meta['xlabel'])
        if 'ylabel' in meta:
            ax.set_ylabel(meta['ylabel'])
        if 'xlim' in meta:
            ax.set_xlim(meta['xlim'])
        if 'ylim' in meta:
            ax.set_ylim(meta['ylim'])
            
        if 'legend' in meta and meta['legend']:
            ax.legend()
        
        # Add a grid for good measure
        ax.grid(True)

    plt.tight_layout()
    plt.show()
    
    return fig, axs
