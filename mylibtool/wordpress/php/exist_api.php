<?php
require_once(dirname(__FILE__).'/wp-load.php');
header('Content-Type:text/json;charset=utf-8');

// Check if an item exist
function check_exist($meta_key, $meta_value) {
	if ($meta_value == "") {
		return false;
	}
		
	$args = array(
	'post_type'=>'post',
	'post_status' => 'any',
	'meta_key' => $meta_key,
	'meta_value' => $meta_value,
	);

	$wp_query=new WP_Query($args);
	if ( $wp_query->have_posts() ) :
		# Video already exist
		return true;
	else: 
		return false;
	endif;
}

$source = $_GET["source"];

if ($source !== Null) {
	if (check_exist('source', $source)) {
		echo "aExist";
	} else {
		echo "aNotExist";
	}
} else {
	echo "Param is empty.";
}
?>