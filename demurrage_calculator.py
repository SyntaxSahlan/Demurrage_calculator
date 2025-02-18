from enum import Enum
from typing import Dict, Tuple

class ContainerType(str, Enum):
    FULL = "FULL"
    REEFER = "REEFER"
    IMCO = "IMCO"
    EMPTY = "EMPTY"

class ContainerSize(str, Enum):
    TWENTY = "20"
    FORTY = "40"

# Free days for each container type
FREE_DAYS = {
    ContainerType.FULL: 10,
    ContainerType.REEFER: 0,
    ContainerType.IMCO: 4,
    ContainerType.EMPTY: 10
}

# Rate structures for different container types and sizes
RATES = {
    ContainerType.FULL: {
        ContainerSize.TWENTY: [(10, 20, 3), (20, 30, 5), (30, float('inf'), 7)],
        ContainerSize.FORTY: [(10, 20, 5), (20, 30, 8), (30, float('inf'), 11)]
    },
    ContainerType.REEFER: {
        ContainerSize.TWENTY: [(0, 10, 6), (10, 20, 8), (20, float('inf'), 10)],
        ContainerSize.FORTY: [(0, 10, 9), (10, 20, 12), (20, float('inf'), 15)]
    },
    ContainerType.IMCO: {
        ContainerSize.TWENTY: [(4, 20, 3), (20, 30, 5), (30, float('inf'), 7)],
        ContainerSize.FORTY: [(4, 20, 5), (20, 30, 8), (30, float('inf'), 11)]
    },
    ContainerType.EMPTY: {
        ContainerSize.TWENTY: [(10, float('inf'), 1.5)],
        ContainerSize.FORTY: [(10, float('inf'), 2.5)]
    }
}
def calculate_demurrage(container_type: ContainerType, 
                container_size: ContainerSize, 
                days: int) -> Tuple[float, Dict]:
    """
    Calculate demurrage charges for a container.
    Returns total charge and breakdown of charges by period.
    """
    if days <= FREE_DAYS[container_type]:
        return 0.0, {}

    total_charge = 0.0
    breakdown = {}

    # Define period names for each container type
    period_names = {
        ContainerType.FULL: ["Initial Storage Period", "Extended Storage Period", "Long-term Storage Period"],
        ContainerType.REEFER: ["Base Storage Period", "Intermediate Storage Period", "Extended Storage Period"],
        ContainerType.IMCO: ["Initial Storage Period", "Extended Storage Period", "Long-term Storage Period"],
        ContainerType.EMPTY: ["Standard Storage Period"]
    }

    rates = RATES[container_type][container_size]
    for i, (period_start, period_end, rate) in enumerate(rates):
        if days <= period_start:
            break
        
        effective_end = min(period_end, days)
        charge_days = effective_end - max(period_start, FREE_DAYS[container_type])
        
        if charge_days > 0:
            charge = charge_days * rate
            period_name = period_names[container_type][min(i, len(period_names[container_type]) - 1)]
            
            breakdown[period_name] = {
                'days': charge_days,
                'rate': rate,
                'charge': charge
            }
            total_charge += charge

    return total_charge, breakdown
