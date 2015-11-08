import os
from . import Module


class ListingModule(Module):
    """Adds additional context with lists of files present in a certain
    directory.
    """

    priority = -5

    def execute(self, builds):
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
            current[parts[-1]] = {
                'type': 'file',
                'parameters': build.parameters
            }
            build.additional_context['listing'] = listing
            build.additional_context['current_listing'] = current
