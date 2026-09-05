def calculate_health_score(
    surface_distance,
    acoustic_level,
    edge_deviation,
    belt_speed,
    carryback_level
):
    """
    Calculates conveyor belt health score out of 100.
    Higher score = healthier condition.
    """

    health_score = 100

    # Surface irregularity penalty
    surface_difference = abs(surface_distance - 100)

    if surface_difference > 15:
        health_score -= 25
    elif surface_difference > 8:
        health_score -= 15
    elif surface_difference > 4:
        health_score -= 5


    # Acoustic abnormality penalty
    if acoustic_level > 75:
        health_score -= 25
    elif acoustic_level > 50:
        health_score -= 15
    elif acoustic_level > 40:
        health_score -= 5


    # Belt edge deviation penalty
    if edge_deviation > 12:
        health_score -= 25
    elif edge_deviation > 6:
        health_score -= 15
    elif edge_deviation > 3:
        health_score -= 5


    # Carryback penalty
    if carryback_level > 0.7:
        health_score -= 20
    elif carryback_level > 0.4:
        health_score -= 10
    elif carryback_level > 0.2:
        health_score -= 5


    # Ensure score remains between 0 and 100
    health_score = max(0, min(100, health_score))

    return health_score


def get_risk_level(health_score):
    """
    Converts health score into risk level.
    """

    if health_score >= 80:
        return "NORMAL"

    elif health_score >= 50:
        return "WARNING"

    else:
        return "CRITICAL"


def get_recommended_action(
    health_score,
    acoustic_level,
    edge_deviation,
    carryback_level
):
    """
    Generates recommended maintenance action.
    """

    actions = []

    if acoustic_level > 75:
        actions.append("Inspect conveyor for abnormal rubbing or impact")

    elif acoustic_level > 50:
        actions.append("Monitor acoustic abnormality closely")


    if edge_deviation > 12:
        actions.append("Immediate belt alignment inspection required")

    elif edge_deviation > 6:
        actions.append("Check belt alignment")


    if carryback_level > 0.7:
        actions.append("Cleaning operation recommended")

    elif carryback_level > 0.4:
        actions.append("Monitor material carryback accumulation")


    if health_score < 50:
        actions.append("Schedule immediate maintenance inspection")

    elif health_score < 80:
        actions.append("Perform preventive inspection")


    if not actions:
        actions.append("System operating normally")


    return actions


def get_recommended_speed(health_score, current_speed):
    """
    Suggests belt speed based on conveyor health.
    """

    if health_score >= 80:
        return round(current_speed, 2)

    elif health_score >= 50:
        return round(current_speed * 0.85, 2)

    else:
        return round(current_speed * 0.65, 2)
if __name__ == "__main__":

    surface_distance = 115
    acoustic_level = 82
    edge_deviation = 15
    belt_speed = 1.5
    carryback_level = 0.8


    health_score = calculate_health_score(
        surface_distance,
        acoustic_level,
        edge_deviation,
        belt_speed,
        carryback_level
    )


    risk_level = get_risk_level(health_score)


    actions = get_recommended_action(
        health_score,
        acoustic_level,
        edge_deviation,
        carryback_level
    )


    recommended_speed = get_recommended_speed(
        health_score,
        belt_speed
    )


    print("CONVEYOR DECISION ENGINE TEST")
    print("-" * 40)

    print("Health Score:", health_score)
    print("Risk Level:", risk_level)
    print("Recommended Speed:", recommended_speed, "m/s")

    print("\nRecommended Actions:")

    for action in actions:
        print("-", action)