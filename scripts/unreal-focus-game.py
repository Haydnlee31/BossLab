import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(world, 0)
unreal.WidgetBlueprintLibrary.set_input_mode_game_only(pc)
pc.set_editor_property('show_mouse_cursor', False)
unreal.log('BossLab focused game input')
