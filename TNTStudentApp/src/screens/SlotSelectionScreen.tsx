import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors } from '../utils/colors';
import { apiService } from '../services/api';
import { Slot, CartItem, RootStackParamList } from '../types';

type SlotSelectionScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'SlotSelection'
>;

interface Props {
  navigation: SlotSelectionScreenNavigationProp;
  route: { params: { vendorId: string; items: CartItem[] } };
}

const SlotSelectionScreen: React.FC<Props> = ({ navigation, route }) => {
  const { vendorId, items } = route.params;
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSlots();
  }, [vendorId]);

  const loadSlots = async () => {
    try {
      const slotData = await apiService.getAvailableSlots(vendorId);
      setSlots(slotData.filter(slot => slot.available));
    } catch (error) {
      console.error('Error loading slots:', error);
      Alert.alert('Error', 'Failed to load available slots');
    } finally {
      setLoading(false);
    }
  };

  const getTotalPrice = () => {
    return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const getTotalItems = () => {
    return items.reduce((sum, item) => sum + item.quantity, 0);
  };

  const proceedToConfirmation = () => {
    if (!selectedSlot) {
      Alert.alert('Error', 'Please select a time slot');
      return;
    }

    const orderData = {
      vendorId,
      slot: selectedSlot,
      items,
      totalPrice: getTotalPrice(),
      totalItems: getTotalItems(),
    };

    navigation.navigate('OrderConfirmation', { orderData: orderData });
  };

  const renderSlot = ({ item }: { item: Slot }) => {
    const isSelected = selectedSlot?.id === item.id;

    return (
      <TouchableOpacity
        style={[styles.slotCard, isSelected && styles.slotCardSelected]}
        onPress={() => setSelectedSlot(item)}
      >
        <View style={styles.slotTime}>
          <Text style={[styles.slotTimeText, isSelected && styles.slotTimeTextSelected]}>
            {item.start_time} - {item.end_time}
          </Text>
        </View>

        <View style={styles.slotInfo}>
          <Text style={[styles.slotCapacity, isSelected && styles.slotCapacitySelected]}>
            {item.available_capacity} slots available
          </Text>
          {isSelected && (
            <Text style={styles.selectedText}>✓ Selected</Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading available slots...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Order Summary */}
      <View style={styles.summary}>
        <Text style={styles.summaryTitle}>Order Summary</Text>
        <Text style={styles.summaryText}>
          {getTotalItems()} items • ₹{getTotalPrice()}
        </Text>
      </View>

      {/* Slots List */}
      <View style={styles.slotsSection}>
        <Text style={styles.sectionTitle}>Select Time Slot</Text>
        {slots.length > 0 ? (
          <FlatList
            data={slots}
            renderItem={renderSlot}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContainer}
            showsVerticalScrollIndicator={false}
          />
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No slots available</Text>
            <Text style={styles.emptySubtext}>Please try again later</Text>
          </View>
        )}
      </View>

      {/* Proceed Button */}
      {selectedSlot && (
        <View style={styles.footer}>
          <TouchableOpacity
            style={styles.proceedButton}
            onPress={proceedToConfirmation}
          >
            <Text style={styles.proceedButtonText}>
              Proceed to Confirmation
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
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
  summary: {
    backgroundColor: colors.surface,
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 8,
  },
  summaryText: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  slotsSection: {
    flex: 1,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 16,
  },
  listContainer: {
    paddingBottom: 20,
  },
  slotCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 2,
    borderColor: colors.border,
  },
  slotCardSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primary + '10', // Light primary background
  },
  slotTime: {
    flex: 1,
  },
  slotTimeText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
  },
  slotTimeTextSelected: {
    color: colors.primary,
  },
  slotInfo: {
    alignItems: 'flex-end',
  },
  slotCapacity: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  slotCapacitySelected: {
    color: colors.primary,
  },
  selectedText: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: 'bold',
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
  footer: {
    backgroundColor: colors.surface,
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  proceedButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  proceedButtonText: {
    color: colors.surface,
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default SlotSelectionScreen;
