import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
  FlatList,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors } from '../utils/colors';
import { apiService } from '../services/api';
import { Vendor, Menu, RootStackParamList } from '../types';

type VendorDetailScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'VendorDetail'
>;

interface Props {
  navigation: VendorDetailScreenNavigationProp;
  route: { params: { vendorId: string } };
}

const VendorDetailScreen: React.FC<Props> = ({ navigation, route }) => {
  const { vendorId } = route.params;
  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [menus, setMenus] = useState<Menu[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVendorData();
  }, [vendorId]);

  const loadVendorData = async () => {
    try {
      const [vendorData, menuData] = await Promise.all([
        apiService.getVendorDetails(vendorId),
        apiService.getVendorMenus(vendorId),
      ]);
      setVendor(vendorData);
      setMenus(menuData);
    } catch (error) {
      console.error('Error loading vendor data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderMenu = ({ item }: { item: Menu }) => (
    <TouchableOpacity
      style={styles.menuCard}
      onPress={() => navigation.navigate('Menu', { vendorId, menuId: item.id })}
    >
      <View style={styles.menuImageContainer}>
        {item.image_url ? (
          <Image source={{ uri: item.image_url }} style={styles.menuImage} />
        ) : (
          <View style={styles.menuImagePlaceholder}>
            <Text style={styles.menuImageText}>
              {item.name.charAt(0).toUpperCase()}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.menuInfo}>
        <Text style={styles.menuName}>{item.name}</Text>
        <Text style={styles.menuDescription} numberOfLines={2}>
          {item.description}
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading vendor details...</Text>
      </View>
    );
  }

  if (!vendor) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Vendor not found</Text>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Vendor Header */}
      <View style={styles.header}>
        <View style={styles.vendorImageContainer}>
          {vendor.image_url ? (
            <Image source={{ uri: vendor.image_url }} style={styles.vendorImage} />
          ) : (
            <View style={styles.vendorImagePlaceholder}>
              <Text style={styles.vendorImageText}>
                {vendor.name.charAt(0).toUpperCase()}
              </Text>
            </View>
          )}
        </View>

        <View style={styles.vendorInfo}>
          <Text style={styles.vendorName}>{vendor.name}</Text>
          <Text style={styles.vendorDescription}>{vendor.description}</Text>
          <View style={styles.vendorMeta}>
            <Text style={styles.vendorRating}>⭐ {vendor.rating}</Text>
            <Text style={styles.vendorDelivery}>
              🕒 {vendor.estimated_delivery} min
            </Text>
          </View>
        </View>
      </View>

      {/* Menus Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Our Menus</Text>
        {menus.length > 0 ? (
          <FlatList
            data={menus}
            renderItem={renderMenu}
            keyExtractor={(item) => item.id}
            scrollEnabled={false}
            showsVerticalScrollIndicator={false}
          />
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No menus available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: colors.textSecondary,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: colors.error,
    marginBottom: 20,
  },
  backButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  backButtonText: {
    color: colors.surface,
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    backgroundColor: colors.surface,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  vendorImageContainer: {
    marginRight: 16,
  },
  vendorImage: {
    width: 100,
    height: 100,
    borderRadius: 16,
  },
  vendorImagePlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  vendorImageText: {
    fontSize: 40,
    fontWeight: 'bold',
    color: colors.surface,
  },
  vendorInfo: {
    flex: 1,
  },
  vendorName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 8,
  },
  vendorDescription: {
    fontSize: 16,
    color: colors.textSecondary,
    marginBottom: 12,
    lineHeight: 22,
  },
  vendorMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  vendorRating: {
    fontSize: 16,
    color: colors.text,
    fontWeight: '500',
  },
  vendorDelivery: {
    fontSize: 16,
    color: colors.success,
    fontWeight: '500',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 16,
  },
  menuCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  menuImageContainer: {
    marginRight: 16,
  },
  menuImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
  },
  menuImagePlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: colors.secondary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  menuImageText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.surface,
  },
  menuInfo: {
    flex: 1,
  },
  menuName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 4,
  },
  menuDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: colors.textSecondary,
  },
});

export default VendorDetailScreen;
