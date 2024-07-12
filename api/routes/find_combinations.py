from flask import Blueprint, request, jsonify

find_combinations_bp = Blueprint('find_combinations_bp', __name__)

# Helper Functions
def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def minutes_to_time_str(minutes):
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}"

def find_best_combinations(flights):
    sorted_flights = sorted(
        [(f['iata'], time_to_minutes(f['duration'])) for f in flights],
        key=lambda x: x[1], reverse=True
    )
    
    target = 168 * 60  # 168 hours in minutes
    combinations = []
    current_combination = []
    current_sum = 0
    
    for iata, duration in sorted_flights:
        if current_sum + duration <= target:
            current_combination.append((iata, duration))
            current_sum += duration
        else:
            if current_combination:
                combinations.append(current_combination)
                current_combination = []
                current_sum = 0
            if duration <= target:
                current_combination.append((iata, duration))
                current_sum = duration
    
    if current_combination:
        combinations.append(current_combination)
    
    optimized_combinations = []
    for combo in combinations:
        optimized_combo = optimize_combination(combo, sorted_flights, target)
        optimized_combinations.append(optimized_combo)
    
    return optimized_combinations

def optimize_combination(combo, all_flights, target):
    combo_sum = sum(duration for _, duration in combo)
    combo_set = set(iata for iata, _ in combo)
    
    available_flights = [(iata, duration) for iata, duration in all_flights if iata not in combo_set]

    best_combo = combo
    best_diff = target - combo_sum
    
    for i, (iata, duration) in enumerate(combo):
        for new_iata, new_duration in available_flights:
            new_combo = combo[:i] + [(new_iata, new_duration)] + combo[i+1:]
            new_sum = sum(duration for _, duration in new_combo)
            if new_sum <= target:
                new_diff = target - new_sum
                if new_diff < best_diff:
                    best_combo = new_combo
                    best_diff = new_diff
                    if best_diff == 0:
                        return best_combo
    
    return best_combo

@find_combinations_bp.route('/find_combinations', methods=['POST'])
def find_combinations():
    flights = request.json.get('flights')
    
    if not flights:
        return jsonify({"error": "No flight data provided"}), 400
    
    best_combinations = find_best_combinations(flights)
    
    result = []
    for i, combo in enumerate(best_combinations, 1):
        total_duration = sum(duration for _, duration in combo)
        result.append({
            "combination": i,
            "flights": [{"iata": iata, "duration": minutes_to_time_str(duration)} for iata, duration in combo],
            "total_duration": minutes_to_time_str(total_duration)
        })
    
    result = sorted(result, key=lambda x: time_to_minutes(x["total_duration"]), reverse=True)
    
    return jsonify({
        "combinations": result,
        "total_combinations": len(best_combinations),
        "exact_168_hour_combinations": sum(1 for combo in best_combinations if sum(duration for _, duration in combo) == 168 * 60)
    })
