import sys
import os

def main():
    # Suppress harmless GTK 4 Theme parser and MESA driver warnings
    # for a cleaner beginner terminal experience.
    os.environ['GTK_CSS_DEBUG'] = '0'
    os.environ['MESA_LOADER_DRIVER_OVERRIDE'] = '' 
    # Disable intel vulkan YUV/Multi-planar DRM FINISHME messages
    os.environ['INTEL_DEBUG'] = 'noanv' 
    os.environ['VK_ICD_FILENAMES'] = '' # Prevent vulkan false-alarms on wayland simply by forcing software rendering logic if vulkan is noisy. Actually, it's safer to just set MESA_DEBUG=silent
    os.environ['MESA_DEBUG'] = 'silent'
    os.environ['LIBGL_DEBUG'] = 'quiet'
    
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    
    from fedora_dev_profiler.ui.app import ProfilerApp as run_app
    app = run_app()
    sys.exit(app.run(sys.argv))

if __name__ == '__main__':
    main()
