ic_file_is_ascii {./icem/vessel.stl}
ic_run_application_exec . icemcfd/output-interfaces stl2df {"./icem/vessel.stl" "./tmpdomain0.uns"  -ascii -fam VESSEL}
ic_empty_tetin 
ic_geo_import_mesh ./tmpdomain0.uns 1 1
ic_boco_solver 
ic_boco_clear_icons 

ic_undo_group_begin 
ic_geo_new_family BODY
ic_boco_set_part_color BODY
ic_undo_group_end 

ic_undo_group_begin 
ic_geo_new_family BODY
ic_boco_set_part_color BODY
ic_set_global geo_cad 0 toptol_userset
ic_set_global geo_cad 0.02 toler

ic_undo_group_begin 
ic_set_global geo_cad 1 toptol_userset
ic_geo_delete_unattached {  VESSEL.PART_ID1 VESSEL.PART_ID2 VESSEL.PART_ID3  ORFN BODY} 0 1
ic_build_topo 0.02 -angle 30 -no_concat  VESSEL.PART_ID1 VESSEL.PART_ID2 VESSEL.PART_ID3  ORFN BODY
ic_geo_delete_unattached {  VESSEL.PART_ID1 VESSEL.PART_ID2 VESSEL.PART_ID3  ORFN BODY}
ic_undo_group_end 

ic_delete_elements family BODY no_undo 1
ic_geo_build_bodies BODY 0 0 0 1 {} 0 0
ic_undo_group_end  

ic_undo_group_begin 
ic_geo_new_family GEOM
ic_boco_set_part_color GEOM
ic_undo_group_end 

ic_undo_group_begin
ic_geo_extract_curves VESSEL.PART_ID2/0 2 20 0
ic_undo_group_end
ic_undo_group_begin
ic_geo_extract_curves VESSEL.PART_ID3/0 2 20 0
ic_undo_group_end

ic_geo_set_family_params BODY no_crv_inf prism 0 hexcore 0 emax 0.3
ic_geo_set_family_params VESSEL.PART_ID1 no_crv_inf prism 1 emax 0.3 ehgt 0 hrat 0 nlay 3 erat 0 ewid 0 emin 0.0 edev 0.0 prism_height_limit 0 law -1 split_wall 0 internal_wall 0
ic_geo_set_family_params VESSEL.PART_ID2 no_crv_inf prism 0 emax 0.1 ehgt 0 hrat 0 nlay 0 erat 0 ewid 0 emin 0.0 edev 0.0 prism_height_limit 0 law -1 split_wall 0 internal_wall 0
ic_geo_set_family_params VESSEL.PART_ID3 no_crv_inf prism 0 emax 0.1 ehgt 0 hrat 0 nlay 0 erat 0 ewid 0 emin 0.0 edev 0.0 prism_height_limit 0 law -1 split_wall 0 internal_wall 0
ic_undo_group_end

ic_geo_params_blank_done part 1
ic_set_global geo_cad 0.02 toler
ic_undo_group_begin 
ic_save_tetin temp_tetra.tin
ic_run_tetra temp_tetra.tin ./tetra_mesh.uns run_cutter 1 delete_auto 1 run_smoother 0 fix_holes 1 n_processors 1 in_process 1 log ./tetra_cmd.log
ic_geo_set_modified 1
ic_boco_solver 
ic_boco_clear_icons 
ic_uns_diagnostic diag_type single quiet 1
ic_smooth_elements map all upto 0.4 iterations 5 fix_families {} n_processors 1 smooth TRI_3 float TETRA_4 laplace 1
ic_smooth_elements map all upto 0.4 iterations 5 prism_warp_weight 0.5 fix_families {} n_processors 1 smooth TETRA_4 float PENTA_6 freeze TRI_3
ic_smooth_elements map all upto 0.4 iterations 5 prism_warp_weight 0.5 fix_families {} metric Quality n_processors 1 smooth TETRA_4 smooth TRI_3 float PENTA_6
ic_geo_set_modified 1
ic_delete_empty_parts 
ic_undo_group_end 

ic_undo_group_begin 
ic_boco_solver {ANSYS Fluent}
ic_solver_mesh_info {ANSYS Fluent}
ic_undo_group_end 

ic_boco_solver 
ic_boco_solver {ANSYS Fluent}
ic_solution_set_solver {ANSYS Fluent} 1

ic_boco_save {./ansys.fbc}
ic_boco_save_atr  {./ansys.atr}
ic_chdir {./}
ic_delete_empty_parts 
ic_delete_empty_parts 
ic_save_tetin project1.tin 0 0 {} {} 0 0 1
ic_uns_check_duplicate_numbers 
ic_uns_renumber_all_elements 1 1
ic_save_unstruct project1.uns 1 {} {} {}
ic_uns_set_modified 1
ic_boco_solver 
ic_boco_solver {ANSYS Fluent}
ic_solution_set_solver {ANSYS Fluent} 1
ic_boco_save project1.fbc
ic_boco_save_atr project1.atr
ic_save_project_file  {./project1.prj} {array\ set\ file_name\ \{ {    catia_dir .} {    parts_dir .} {    domain_loaded 0} {    cart_file_loaded 0} {    cart_file {}} {    domain_saved project1.uns} {    archive {}} {    med_replay {}} {    topology_dir .} {    ugparts_dir .} {    icons {{$env(icem_ACN)/lib/ai_env/icons} {$env(icem_ACN)/lib/va/EZCAD/icons} {$env(icem_ACN)/lib/icons} {$env(icem_ACN)/lib/va/CABIN/icons}}} {    tetin project1.tin} {    family_boco project1.fbc} {    prism_params ./Quentin.prism_params} {    iges_dir .} {    solver_params_loaded 0} {    attributes_loaded 0} {    project_lock {}} {    attributes project1.atr} {    domain project1.uns} {    domains_dir .} {    settings_loaded 0} {    settings project1.prj} {    blocking {}} {    hexa_replay {}} {    transfer_dir .} {    mesh_dir .} {    family_topo {}} {    gemsparts_dir .} {    family_boco_loaded 0} {    tetin_loaded 1} {    project_dir .} {    topo_mulcad_out {}} {    solver_params {}} \} array\ set\ options\ \{ {    expert 1} {    remote_path {}} {    tree_disp_quad 2} {    tree_disp_pyra 0} {    evaluate_diagnostic 0} {    histo_show_default 1} {    select_toggle_corners 0} {    remove_all 0} {    keep_existing_file_names 0} {    record_journal 0} {    edit_wait 0} {    face_mode all} {    select_mode all} {    med_save_emergency_tetin 1} {    user_name Quentin} {    diag_which all} {    uns_warn_if_display 500000} {    bubble_delay 1000} {    external_num 1} {    tree_disp_tri 2} {    apply_all 0} {    default_solver {ANSYS Fluent}} {    temporary_directory {}} {    flood_select_angle 0} {    home_after_load 1} {    project_active 0} {    histo_color_by_quality_default 1} {    undo_logging 1} {    tree_disp_hexa 0} {    histo_solid_default 1} {    host_name Quentin} {    xhidden_full 1} {    replay_internal_editor 1} {    editor {}} {    mouse_color orange} {    clear_undo 1} {    remote_acn {}} {    remote_sh csh} {    tree_disp_penta 0} {    n_processors 1} {    remote_host {}} {    save_to_new 0} {    quality_info Quality} {    tree_disp_node 0} {    med_save_emergency_mesh 1} {    redtext_color red} {    tree_disp_line 0} {    select_edge_mode 0} {    use_dlremote 0} {    max_mesh_map_size 1024} {    show_tris 1} {    remote_user {}} {    enable_idle 0} {    auto_save_views 1} {    max_cad_map_size 512} {    display_origin 0} {    uns_warn_user_if_display 1000000} {    detail_info 0} {    win_java_help 0} {    show_factor 1} {    boundary_mode all} {    clean_up_tmp_files 1} {    auto_fix_uncovered_faces 1} {    med_save_emergency_blocking 1} {    max_binary_tetin 0} {    tree_disp_tetra 0} \} array\ set\ disp_options\ \{ {    uns_dualmesh 0} {    uns_warn_if_display 500000} {    uns_normals_colored 0} {    uns_icons 0} {    uns_locked_elements 0} {    uns_shrink_npos 0} {    uns_node_type None} {    uns_icons_normals_vol 0} {    uns_bcfield 0} {    backup Solid/wire} {    uns_nodes 0} {    uns_only_edges 0} {    uns_surf_bounds 0} {    uns_wide_lines 0} {    uns_vol_bounds 0} {    uns_displ_orient Triad} {    uns_orientation 0} {    uns_directions 0} {    uns_thickness 0} {    uns_shell_diagnostic 0} {    uns_normals 0} {    uns_couplings 0} {    uns_periodicity 0} {    uns_single_surfaces 0} {    uns_midside_nodes 1} {    uns_shrink 100} {    uns_multiple_surfaces 0} {    uns_no_inner 0} {    uns_enums 0} {    uns_disp Wire} {    uns_bcfield_name {}} {    uns_color_by_quality 0} {    uns_changes 0} {    uns_cut_delay_count 1000} \} {set icon_size1 24} {set icon_size2 35} {set thickness_defined 0} {set solver_type 1} {set solver_setup -1} array\ set\ prism_values\ \{ {    n_triangle_smoothing_steps 5} {    min_smoothing_steps 6} {    first_layer_smoothing_steps 1} {    new_volume BODY} {    height 9.9999997e-06} {    prism_height_limit 0} {    interpolate_heights 0} {    n_tetra_smoothing_steps 10} {    do_checks {}} {    delete_standalone 1} {    ortho_weight 0.50} {    max_aspect_ratio {}} {    ratio_max {}} {    incremental_write 0} {    total_height 0} {    use_prism_v10 0} {    intermediate_write 1} {    delete_base_triangles {}} {    ratio_multiplier {}} {    verbosity_level 1} {    refine_prism_boundary 1} {    max_size_ratio {}} {    triangle_quality {}} {    max_prism_angle 180} {    tetra_smooth_limit 0.30000001} {    max_jump_factor 5} {    use_existing_quad_layers 0} {    layers 5} {    fillet 0.1} {    into_orphan 0} {    init_dir_from_prev {}} {    blayer_2d 0} {    do_not_allow_sticking {}} {    top_family {}} {    law exponential} {    min_smoothing_val 0.1} {    auto_reduction 0} {    max_prism_height_ratio 0} {    stop_columns 1} {    stair_step 1} {    smoothing_steps 12} {    side_family {}} {    min_prism_quality 0.0099999998} {    ratio 1.2} \} {set aie_current_flavor {}} array\ set\ vid_options\ \{ {    wb_import_mat_points 0} {    wb_NS_to_subset 0} {    wb_import_surface_bodies 1} {    wb_import_cad_att_pre {SDFEA;DDM}} {    wb_import_mix_res_line 0} {    wb_import_tritol 0.001} {    auxiliary 0} {    wb_import_cad_att_trans 1} {    wb_import_mix_res -1} {    wb_import_mix_res_surface 0} {    show_name 0} {    wb_import_solid_bodies 1} {    wb_import_delete_solids 0} {    wb_import_mix_res_solid 0} {    wb_import_save_pmdb {}} {    inherit 1} {    default_part GEOM} {    new_srf_topo 1} {    wb_import_associativity_model_name {}} {    DelPerFlag 0} {    show_item_name 0} {    wb_import_line_bodies 0} {    wb_import_save_partfile 0} {    wb_import_analysis_type 3} {    composite_tolerance 1.0} {    wb_NS_to_entity_parts 0} {    wb_import_en_sym_proc 1} {    wb_run_mesher tetra} {    wb_import_sel_proc 1} {    wb_import_work_points 0} {    wb_import_reference_key 0} {    wb_import_mix_res_point 0} {    wb_import_pluginname {}} {    wb_NS_only 0} {    wb_import_create_solids 0} {    wb_import_refresh_pmdb 0} {    wb_import_lcs 0} {    wb_import_sel_pre {}} {    wb_import_scale_geo Default} {    wb_import_load_pmdb {}} {    replace 0} {    wb_import_transfer_file_scale 1.0} {    wb_import_cad_associativity 0} {    same_pnt_tol 1e-4} {    tdv_axes 1} {    vid_mode 0} {    DelBlkPerFlag 0} \} {set savedTreeVisibility {geomNode 2 geom_subsetNode 2 geomCurveNode 2 geomSurfNode 2 geomBodyNode 2 meshNode 1 mesh_subsetNode 2 meshLineNode 0 meshShellNode 2 meshTriNode 2 meshVolumeNode 0 meshTetraNode 0 partNode 2  part-BODY 2  part-VESSEL.PART_ID1 2 part-VESSEL.PART_ID2 2 part-VESSEL.PART_ID3 2 }} {set last_view {rot {-0.313596488594 -0.414653227352 -0.0233356196303 0.853917672988} scale {31.1498270472 31.1498270472 31.1498270472} center {9.46595 -29.78375 -279.4645} pos {0 0 0}}} array\ set\ cut_info\ \{ {    active 0} \} array\ set\ hex_option\ \{ {    default_bunching_ratio 2.0} {    floating_grid 0} {    project_to_topo 0} {    n_tetra_smoothing_steps 20} {    sketching_mode 0} {    trfDeg 1} {    wr_hexa7 0} {    smooth_ogrid 0} {    find_worst 1-3} {    hexa_verbose_mode 0} {    old_eparams 0} {    uns_face_mesh_method uniform_quad} {    multigrid_level 0} {    uns_face_mesh one_tri} {    check_blck 0} {    proj_limit 0} {    check_inv 0} {    project_bspline 0} {    hexa_update_mode 1} {    default_bunching_law BiGeometric} {    worse_criterion Quality} \} array\ set\ saved_views\ \{ {    views {}} \}} {icem CFD}


ic_exec {/softwares/ansys-2019/v190/icemcfd/linux64_amd/icemcfd/output-interfaces/fluent6} -dom ./project1.uns -b project1.fbc ./fluent
ic_uns_num_couplings 

ic_undo_group_begin 
ic_uns_create_diagnostic_edgelist 1
ic_uns_diagnostic subset all diag_type uncovered fix_fam FIX_UNCOVERED diag_verb {Uncovered faces} fams {} busy_off 1 quiet 1
ic_uns_create_diagnostic_edgelist 0
ic_undo_group_end 

ic_uns_min_metric Quality {} {}
exit
