<?php
/**
 * WooCommerce Integration for Measurement Profiles
 *
 * @package MeasurementProfiles
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * MP_WooCommerce class
 */
class MP_WooCommerce {

    /**
     * Constructor
     */
    public function __construct() {
        add_action( 'add_meta_boxes', array( $this, 'add_product_meta_box' ) );
        add_action( 'save_post_product', array( $this, 'save_product_meta' ) );
        add_action( 'woocommerce_before_add_to_cart_button', array( $this, 'display_measurement_form' ) );
        add_filter( 'woocommerce_add_cart_item_data', array( $this, 'add_cart_item_data' ), 10, 2 );
        add_filter( 'woocommerce_get_item_data', array( $this, 'get_item_data' ), 10, 2 );
        add_action( 'woocommerce_checkout_create_order_line_item', array( $this, 'add_order_item_meta' ), 10, 4 );
        add_filter( 'woocommerce_add_to_cart_validation', array( $this, 'validate_add_to_cart' ), 10, 3 );
        add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_frontend_assets' ) );
    }

    /**
     * Add meta box to product edit page
     */
    public function add_product_meta_box() {
        add_meta_box(
            'mp_measurement_profiles',
            __( 'Measurement Profiles', 'measurement-profiles' ),
            array( $this, 'render_product_meta_box' ),
            'product',
            'side'
        );
    }

    /**
     * Render product meta box
     */
    public function render_product_meta_box( $post ) {
        $enabled = get_post_meta( $post->ID, '_mp_measurement_enabled', true );
        $selected_profiles = get_post_meta( $post->ID, '_mp_measurement_profiles', true ) ?: array();
        $profiles = MP_Core::get_profiles();

        wp_nonce_field( 'mp_product_meta', 'mp_product_meta_nonce' );

        ?>
        <p>
            <label>
                <input type="checkbox" name="_mp_measurement_enabled" value="1" <?php checked( $enabled, '1' ); ?>>
                <?php _e( 'Enable measurement profiles for this product', 'measurement-profiles' ); ?>
            </label>
        </p>
        <p><?php _e( 'Select profiles to enable:', 'measurement-profiles' ); ?></p>
        <?php foreach ( $profiles as $slug => $profile ) : ?>
            <label>
                <input type="checkbox" name="_mp_measurement_profiles[]" value="<?php echo esc_attr( $slug ); ?>" <?php checked( in_array( $slug, $selected_profiles ) ); ?>>
                <?php echo esc_html( $profile['name'] ); ?>
            </label><br>
        <?php endforeach; ?>
        <?php
    }

    /**
     * Save product meta
     */
    public function save_product_meta( $post_id ) {
        if ( ! isset( $_POST['mp_product_meta_nonce'] ) || ! wp_verify_nonce( $_POST['mp_product_meta_nonce'], 'mp_product_meta' ) ) {
            return;
        }

        if ( isset( $_POST['_mp_measurement_enabled'] ) ) {
            update_post_meta( $post_id, '_mp_measurement_enabled', '1' );
        } else {
            delete_post_meta( $post_id, '_mp_measurement_enabled' );
        }

        $profiles = isset( $_POST['_mp_measurement_profiles'] ) ? array_map( 'sanitize_key', $_POST['_mp_measurement_profiles'] ) : array();
        update_post_meta( $post_id, '_mp_measurement_profiles', $profiles );
    }

    /**
     * Display measurement form on product page
     */
    public function display_measurement_form() {
        global $product;
        $enabled = get_post_meta( $product->get_id(), '_mp_measurement_enabled', true );
        if ( ! $enabled ) {
            return;
        }

        $selected_profiles = get_post_meta( $product->get_id(), '_mp_measurement_profiles', true ) ?: array();
        if ( empty( $selected_profiles ) ) {
            return;
        }

        $profiles = MP_Core::get_profiles();
        $available_profiles = array_intersect_key( $profiles, array_flip( $selected_profiles ) );
        if ( empty( $available_profiles ) ) {
            return;
        }

        ?>
        <div class="mp-measurement-form">
            <h3><?php _e( 'Measurement Profile', 'measurement-profiles' ); ?></h3>
            <select name="mp_profile" id="mp-profile-select" required>
                <option value=""><?php _e( 'Select Profile', 'measurement-profiles' ); ?></option>
                <?php foreach ( $available_profiles as $slug => $profile ) : ?>
                    <option value="<?php echo esc_attr( $slug ); ?>"><?php echo esc_html( $profile['name'] ); ?></option>
                <?php endforeach; ?>
            </select>
            <div id="mp-fields-container"></div>
        </div>
        <?php
    }

    /**
     * Enqueue frontend assets
     */
    public function enqueue_frontend_assets() {
        if ( ! is_product() ) {
            return;
        }

        wp_enqueue_script( 'mp-frontend-js', MP_PLUGIN_URL . 'assets/js/frontend.js', array( 'jquery' ), MP_VERSION, true );
        wp_enqueue_style( 'mp-frontend-css', MP_PLUGIN_URL . 'assets/css/frontend.css', array(), MP_VERSION );

        wp_localize_script( 'mp-frontend-js', 'mpFrontend', array(
            'ajaxUrl' => admin_url( 'admin-ajax.php' ),
            'nonce'   => wp_create_nonce( 'mp_frontend_nonce' ),
        ) );
    }

    /**
     * Add cart item data
     */
    public function add_cart_item_data( $cart_item_data, $product_id ) {
        if ( isset( $_POST['mp_profile'] ) && ! empty( $_POST['mp_profile'] ) ) {
            $cart_item_data['mp_profile'] = sanitize_key( $_POST['mp_profile'] );
            $cart_item_data['mp_measurements'] = isset( $_POST['mp_measurements'] ) ? array_map( 'sanitize_text_field', $_POST['mp_measurements'] ) : array();
            $cart_item_data['unique_key'] = md5( microtime() . rand() );
        }
        return $cart_item_data;
    }

    /**
     * Get item data for cart display
     */
    public function get_item_data( $item_data, $cart_item ) {
        if ( isset( $cart_item['mp_profile'] ) ) {
            $profile = MP_Core::get_profile( $cart_item['mp_profile'] );
            $item_data[] = array(
                'name'  => __( 'Fit Profile', 'measurement-profiles' ),
                'value' => $profile ? $profile['name'] : $cart_item['mp_profile'],
            );

            if ( ! empty( $cart_item['mp_measurements'] ) ) {
                $measurements = '';
                $fields = MP_Core::get_available_fields();
                foreach ( $cart_item['mp_measurements'] as $field_id => $value ) {
                    if ( isset( $fields[ $field_id ] ) ) {
                        $measurements .= $fields[ $field_id ]['label'] . ': ' . $value . ' ' . $fields[ $field_id ]['unit'] . '<br>';
                    }
                }
                $item_data[] = array(
                    'name'  => __( 'Measurements', 'measurement-profiles' ),
                    'value' => $measurements,
                );
            }
        }
        return $item_data;
    }

    /**
     * Add order item meta
     */
    public function add_order_item_meta( $item, $cart_item_key, $values, $order ) {
        if ( isset( $values['mp_profile'] ) ) {
            $profile = MP_Core::get_profile( $values['mp_profile'] );
            $item->add_meta_data( __( 'Fit Profile', 'measurement-profiles' ), $profile ? $profile['name'] : $values['mp_profile'] );

            if ( ! empty( $values['mp_measurements'] ) ) {
                $measurements = '';
                $fields = MP_Core::get_available_fields();
                foreach ( $values['mp_measurements'] as $field_id => $value ) {
                    if ( isset( $fields[ $field_id ] ) ) {
                        $measurements .= $fields[ $field_id ]['label'] . ': ' . $value . ' ' . $fields[ $field_id ]['unit'] . "\n";
                    }
                }
                $item->add_meta_data( __( 'Measurements', 'measurement-profiles' ), $measurements );
            }
        }
    }

    /**
     * Validate add to cart
     */
    public function validate_add_to_cart( $passed, $product_id, $quantity ) {
        $enabled = get_post_meta( $product_id, '_mp_measurement_enabled', true );
        if ( $enabled ) {
            if ( empty( $_POST['mp_profile'] ) ) {
                wc_add_notice( __( 'Please select a measurement profile.', 'measurement-profiles' ), 'error' );
                $passed = false;
            } else {
                $profile = MP_Core::get_profile( $_POST['mp_profile'] );
                if ( $profile ) {
                    $enabled_fields = $profile['enabled_fields'];
                    if ( ! empty( $enabled_fields ) ) {
                        foreach ( $enabled_fields as $field_id ) {
                            if ( empty( $_POST['mp_measurements'][ $field_id ] ) ) {
                                wc_add_notice( __( 'Please enter all required measurements.', 'measurement-profiles' ), 'error' );
                                $passed = false;
                                break;
                            }
                        }
                    }
                }
            }
        }
        return $passed;
    }
}
