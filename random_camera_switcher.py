import obspython as obs
import random

# Set this to True for webcams, False for photos
use_webcams = True

def script_description():
    return "Random Camera Switcher: Switches between Camera 1-4 (webcams or photos)"

def script_update(settings):
    global use_webcams
    use_webcams = obs.obs_data_get_bool(settings, "use_webcams")

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "use_webcams", "Use Webcams (uncheck for photos)")
    return props

def switch_camera():
    global use_webcams
    source_type = "dshow_input" if use_webcams else "image_source"
    source_names = ["Camera 1", "Camera 2", "Camera 3"]

    current_scene = obs.obs_frontend_get_current_scene()
    if not current_scene:
        print("No current scene")
        return

    scene = obs.obs_scene_from_source(current_scene)
    if not scene:
        print("Failed to get scene from source")
        obs.obs_source_release(current_scene)
        return

    # Hide all existing camera sources in the scene
    items = obs.obs_scene_enum_items(scene)
    for item in items:
        source = obs.obs_sceneitem_get_source(item)
        if obs.obs_source_get_name(source) in source_names:
            obs.obs_sceneitem_set_visible(item, False)
    obs.sceneitem_list_release(items)

    # Find all matching sources
    all_sources = obs.obs_enum_sources()
    matching_sources = [s for s in all_sources if obs.obs_source_get_id(s) == source_type and obs.obs_source_get_name(s) in source_names]

    if not matching_sources:
        print(f"No {'webcam' if use_webcams else 'photo'} sources named Camera 1-4 found")
        obs.obs_source_release(current_scene)
        obs.source_list_release(all_sources)
        return

    # Show a random camera source in the scene
    random_source = random.choice(matching_sources)
    random_source_name = obs.obs_source_get_name(random_source)
    
    items = obs.obs_scene_enum_items(scene)
    for item in items:
        source = obs.obs_sceneitem_get_source(item)
        if obs.obs_source_get_name(source) == random_source_name:
            obs.obs_sceneitem_set_visible(item, True)
            print(f"Switched to: {random_source_name}")
            break
    else:
        # If the source isn't in the scene, add it
        scene_item = obs.obs_scene_add(scene, random_source)
        if scene_item:
            print(f"Added and switched to: {random_source_name}")
        else:
            print("Failed to add source to scene")
    obs.sceneitem_list_release(items)

    obs.obs_source_release(current_scene)
    obs.source_list_release(all_sources)

def set_next_switch():
    global switch_timer
    
    # Cancel any existing timer
    obs.remove_current_callback()
    
    # Set a new timer for a random duration between 30 and 120 seconds
    duration = random.randint(30, 120)
    switch_timer = obs.timer_add(switch_camera, duration * 1000)

def script_load(settings):
    set_next_switch()

def script_unload():
    obs.remove_current_callback()