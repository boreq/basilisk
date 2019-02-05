import os
from ..module import Module


class ListingModule(Module):
    """Adds additional context with lists of files which will be created in the
    output directory. Those lists can be used to create file listings such as
    navigation menus or article lists in the templates. The following keys are
    additionaly available in the context: 'listing', 'current_listing'.

    Example of the additional context:

        {
            'listing': {
                'about': {
                    'type': 'directory',
                    'content': {
                        'index.html': {
                            'type': 'file',
                            'parameters': {'title': 'Contact'}
                        }
                    }
                },
                'index.html': {
                    'type': 'file'},
                    'parameters': {'title': 'Simple example'}
                }
            },
            'current_listing': {
                'index.html': {
                    'type': 'file',
                    'parameters': {'title': 'Contact'}
                }
            }
        }

    The listing shows all files which most likely will be present in the output
    directory (it is possible that a module which runs after this one will
    modify them). Since this example listing is shown for a file
    'about/index.html', the current listing provides a shortcut to view the list
    of files in that particular directory (only that file is present however).

    This module doesn't require any additional configuration.
    """

    def postprocess(self, builds):
        listing = {}
        for build in builds:
            parts = build.output_path.split(os.sep)
            current = listing
            for part in parts[:-1]:
                if not part in current:
                    current[part] = {
                        'type': 'directory',
                        'content': {}
                    }
                current = current[part]['content']

            # Here we have to cheat a little to get the params by reading the
            # file at this point.
            inpath = os.path.join(self.builder.source_directory, build.input_path)
            lines = build.read(inpath)
            content, parameters = build.parse_lines(lines)

            current[parts[-1]] = {
                'type': 'file',
                'parameters': parameters
            }

            # Put the created listings the the additional context.
            build.additional_context['listing'] = listing
            build.additional_context['current_listing'] = current
