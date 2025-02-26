import random
from models import DebtorProfile, CommunicationState

def generate_samples(num_samples=10):
    """
    Generate synthetic sample profiles with only essential fields initialized.

    :param num_samples: Number of samples to generate
    :return: A list of sample DebtorProfile instances
    """
    communication_states = [CommunicationState.ENGAGED, CommunicationState.NO_RESPONE]
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie"]
    last_names = ["Doe", "Smith", "Brown", "Johnson", "Davis"]

    samples = []

    for _ in range(num_samples):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        communication_state = random.choice(communication_states)
        income = random.uniform(500, 5000)
        outstanding_balance = random.uniform(500, 10000)
        overdue_days = random.randint(0, 180)

        sample_profile = DebtorProfile(
            communication_state=communication_state,
            name=name,
            income=income,
            outstanding_balance=outstanding_balance,
            overdue_days=overdue_days,
            risk_level=None,
            installment_plan=None
        )

        samples.append(sample_profile)

    return samples
