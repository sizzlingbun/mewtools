// insert metadata for RestApi
add_action("rest_insert_post", function ($post, $request, $creating) {

	// Set metadata
	$metas = $request->get_param("metadata");

    if (is_array($metas)) {

        foreach ($metas as $name => $value) {
            update_post_meta($post->ID, $name, $value);
        }

    }
}, 10, 3);