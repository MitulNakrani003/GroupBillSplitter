class Participant:
    def __init__(self, name):
        self.name = name
        self.total_due = 0.0

    def add_to_total(self, amount):
        self.total_due += amount

class Item:
    def __init__(self, name, price, participants):
        self.name = name
        self.price = price
        self.participants = participants

class Bill:
    def __init__(self, description):
        self.description = description
        self.items = []
        self.participants = {}

    def add_participant(self, name):
        """Adds a participant to the bill if they don't already exist."""
        if name and name not in self.participants:
            self.participants[name] = Participant(name)

    def _recalculate_totals(self):
        """Helper method to clear and recalculate all participant totals."""
        # Reset all totals to zero
        for participant in self.participants.values():
            participant.total_due = 0.0
        
        # Recalculate from scratch based on current items
        for item in self.items:
            price = item['price']
            participant_names = item['participants']
            if participant_names:
                split_amount = price / len(participant_names)
                for name in participant_names:
                    # Ensure participant exists before adding to total
                    if name in self.participants:
                        self.participants[name].add_to_total(split_amount)

    def add_item(self, item_name, price, participant_names):
        self.items.append({'item_name': item_name, 'price': price, 'participants': participant_names})
        # Ensure all participants involved in the item exist in the bill's participant list
        for name in participant_names:
            if name not in self.participants:
                self.participants[name] = Participant(name)
        
        self._recalculate_totals()

    def remove_item(self, item_name_to_remove):
        """Removes an item from the bill by its name and recalculates totals."""
        # Find the item to remove
        item_found = None
        for item in self.items:
            if item['item_name'] == item_name_to_remove:
                item_found = item
                break
        
        if item_found:
            self.items.remove(item_found)
            # After removing, we must recalculate everyone's total
            self._recalculate_totals()
            return True
        return False


    def get_totals(self):
        return {name: participant.total_due for name, participant in self.participants.items()}