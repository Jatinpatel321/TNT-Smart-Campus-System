import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
  RefreshControl,
  TextInput,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors } from '../utils/colors';
import { apiService } from '../services/api';
import { Vendor, RootStackParamList } from '../types';

type VendorListScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'VendorList'
>;

interface Props {
  navigation: VendorListScreenNavigationProp;
}

const VendorListScreen: React.FC<Props> = ({ navigation }) => {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadVendors();
  }, []);

  const loadVendors = async () => {
    try {
      const vendorData = await apiService.getVendors();
      setVendors(vendorData);
    } catch (error) {
      console.error('Error loading vendors:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadVendors();
  };

  const renderVendor = ({ item }: { item: Vendor }) => (
    <TouchableOpacity
      style={styles.vendorCard}
      onPress={() => navigation.navigate('VendorDetail', { vendorId: item.id })}
    >
      <View style={styles.vendorImageContainer}>
        {item.image_url ? (
          <Image source={{ uri: item.image_url }} style={styles.vendorImage} />
        ) : (
          <View style={styles.vendorImagePlaceholder}>
            <Text style={styles.vendorImageText}>
              {item.name.charAt(0).toUpperCase()}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.vendorInfo}>
        <Text style={styles.vendorName}>{item.name}</Text>
        <Text style={styles.vendorDescription} numberOfLines={2}>
          {item.description}
        </Text>
        <View style={styles.vendorMeta}>
          <Text style={styles.vendorRating}>⭐ {item.rating}</Text>
          <Text style={styles.vendorDelivery}>
            🕒 {item.estimated_delivery} min
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading vendors...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🍽️ TNT</Text>
        <Text style={styles.headerSubtitle}>Choose your favorite vendor</Text>
      </View>

      <FlatList
        data={vendors}
        renderItem={renderVendor}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[colors.primary]}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No vendors available</Text>
            <Text style={styles.emptySubtext}>Please check back later</Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: 20,
    paddingBottom: 10,
    backgroundColor: colors.surface,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.primary,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 4,
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
  listContainer: {
    padding: 16,
  },
  vendorCard: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    marginBottom: 16,
    padding: 16,
    flexDirection: 'row',
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  vendorImageContainer: {
    marginRight: 16,
  },
  vendorImage: {
    width: 80,
    height: 80,
    borderRadius: 12,
  },
  vendorImagePlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 12,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  vendorImageText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.surface,
  },
  vendorInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  vendorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 4,
  },
  vendorDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
    lineHeight: 20,
  },
  vendorMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  vendorRating: {
    fontSize: 14,
    color: colors.text,
    fontWeight: '500',
  },
  vendorDelivery: {
    fontSize: 14,
    color: colors.success,
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 16,
    color: colors.textSecondary,
  },
});

export default VendorListScreen;
