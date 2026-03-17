from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import WeightLog, DailyLog
from datetime import datetime, date, timedelta
from collections import defaultdict

main = Blueprint('main', __name__)

# ── Home ─────────────────────────────────────────────────────────────────────
@main.route('/')
def index():
    return render_template('index.html')

# ── Dashboard ────────────────────────────────────────────────────────────────
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# ── Workout ──────────────────────────────────────────────────────────────────
@main.route('/workout')
@login_required
def workout():
    return render_template('workout.html', user=current_user)

# ── Diet ─────────────────────────────────────────────────────────────────────
@main.route('/diet')
@login_required
def diet():
    return render_template('diet.html', user=current_user)

# ── Progress ─────────────────────────────────────────────────────────────────
@main.route('/progress', methods=['GET', 'POST'])
@login_required
def progress():
    if request.method == 'POST':
        action = request.form.get('action')

        # Save profile stats
        if action == 'save_profile':
            try:
                current_user.height      = float(request.form.get('height', 0))
                current_user.age         = int(request.form.get('age', 0))
                current_user.goal_weight = float(request.form.get('goal_weight', 0))
                if not current_user.start_weight:
                    current_user.start_weight = float(request.form.get('start_weight', 0))
                db.session.commit()
                flash('Profile updated!', 'success')
            except Exception as e:
                flash('Please enter valid numbers.', 'error')
            return redirect(url_for('main.progress'))

        # Log weight
        if action == 'log_weight':
            try:
                weight = float(request.form.get('weight', 0))
                if weight <= 0:
                    flash('Please enter a valid weight.', 'error')
                    return redirect(url_for('main.progress'))

                # Check if already logged today
                today = date.today()
                existing = WeightLog.query.filter_by(user_id=current_user.id).filter(
                    db.func.date(WeightLog.logged_at) == today
                ).first()

                if existing:
                    existing.weight = weight
                    flash('Today\'s weight updated!', 'success')
                else:
                    log = WeightLog(user_id=current_user.id, weight=weight)
                    db.session.add(log)
                    flash('Weight logged!', 'success')

                db.session.commit()
            except:
                flash('Something went wrong. Try again.', 'error')
            return redirect(url_for('main.progress'))

    # GET — build data for page
    logs = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.logged_at).all()

    # Chart data
    chart_labels  = [l.logged_at.strftime('%d %b') for l in logs]
    chart_weights = [l.weight for l in logs]

    # Progress stats
    current_weight = logs[-1].weight if logs else None
    start_weight   = current_user.start_weight
    goal_weight    = current_user.goal_weight

    # BMI
    bmi = None
    bmi_category = None
    if current_weight and current_user.height:
        h_m = current_user.height / 100
        bmi = round(current_weight / (h_m * h_m), 1)
        if bmi < 18.5:   bmi_category = ('Underweight', 'bmi-low')
        elif bmi < 25:   bmi_category = ('Normal',      'bmi-normal')
        elif bmi < 30:   bmi_category = ('Overweight',  'bmi-high')
        else:            bmi_category = ('Obese',        'bmi-very-high')

    # Change stats
    total_change = None
    remaining    = None
    progress_pct = 0
    if current_weight and start_weight and goal_weight:
        total_change = round(current_weight - start_weight, 1)
        remaining    = round(current_weight - goal_weight, 1)
        total_journey = abs(goal_weight - start_weight)
        if total_journey > 0:
            covered     = abs(current_weight - start_weight)
            progress_pct = min(100, round((covered / total_journey) * 100))

    # Weight history table (last 14 entries, newest first)
    history = list(reversed(logs[-14:]))
    history_data = []
    for i, log in enumerate(history):
        prev_weight = history[i+1].weight if i+1 < len(history) else None
        diff = None
        if prev_weight:
            diff = round(log.weight - prev_weight, 1)
        history_data.append({ 'date': log.logged_at.strftime('%d %b %Y'), 'weight': log.weight, 'diff': diff })

    # Weekly trend (last 7 days vs previous 7)
    trend_text    = None
    trend_class   = ''
    insight_msg   = None
    streak        = 0

    if len(logs) >= 2:
        # Streak — consecutive days logged
        all_dates = sorted(set(l.logged_at.date() for l in logs), reverse=True)
        streak = 1
        for i in range(1, len(all_dates)):
            if (all_dates[i-1] - all_dates[i]).days == 1:
                streak += 1
            else:
                break

        # Weekly rate
        if len(logs) >= 7:
            week_ago_weight = logs[-7].weight
            weekly_change   = round(logs[-1].weight - week_ago_weight, 2)
            if weekly_change < -0.1:
                trend_text  = f'Losing {abs(weekly_change)}kg/week'
                trend_class = 'trend-down'
            elif weekly_change > 0.1:
                trend_text  = f'Gaining {weekly_change}kg/week'
                trend_class = 'trend-up'
            else:
                trend_text  = 'Weight stable this week'
                trend_class = 'trend-flat'

            # Smart insight
            if goal_weight and current_weight:
                losing = goal_weight < start_weight if start_weight else True
                if losing:
                    if weekly_change < -1.0:
                        insight_msg = '⚠️ Losing too fast. Aim for 0.3–0.7kg/week to preserve muscle.'
                    elif -0.7 <= weekly_change <= -0.2:
                        insight_msg = '✅ Perfect rate. Keep going consistently.'
                    elif weekly_change > 0:
                        insight_msg = '📈 Weight going up while goal is to lose. Review your diet.'
                else:
                    if weekly_change > 1.0:
                        insight_msg = '⚠️ Gaining too fast. Slow down to minimize fat gain.'
                    elif 0.2 <= weekly_change <= 0.7:
                        insight_msg = '✅ Solid bulk rate. Stay consistent.'
                    elif weekly_change < 0:
                        insight_msg = '📉 Weight dropping while goal is to gain. Eat more.'

    # ETA to goal
    eta_text = None
    if current_weight and goal_weight and len(logs) >= 7:
        weekly_change = logs[-1].weight - logs[-7].weight
        if weekly_change != 0:
            weeks_needed = abs((current_weight - goal_weight) / weekly_change)
            eta_date     = date.today() + timedelta(weeks=weeks_needed)
            eta_text     = eta_date.strftime('%B %Y')

    return render_template('progress.html',
        user=current_user,
        logs=logs,
        chart_labels=chart_labels,
        chart_weights=chart_weights,
        current_weight=current_weight,
        bmi=bmi,
        bmi_category=bmi_category,
        total_change=total_change,
        remaining=remaining,
        progress_pct=progress_pct,
        history_data=history_data,
        trend_text=trend_text,
        trend_class=trend_class,
        insight_msg=insight_msg,
        streak=streak,
        eta_text=eta_text,
    )

# ── Daily Log ────────────────────────────────────────────────────────────────
@main.route('/daily-log', methods=['GET', 'POST'])
@login_required
def daily_log():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'save_split':
            current_user.split_pref = request.form.get('split')
            db.session.commit()
            flash('Split preference saved!', 'success')
            return redirect(url_for('main.daily_log'))

        if action == 'save_log':
            try:
                today    = date.today()
                rating   = int(request.form.get('rating', 0))
                completion = request.form.get('completion', 'rest')
                note     = request.form.get('note', '').strip()[:300]

                existing = DailyLog.query.filter_by(user_id=current_user.id, date=today).first()
                if existing:
                    existing.strength_rating = rating
                    existing.completion      = completion
                    existing.note            = note
                    flash('Today\'s log updated!', 'success')
                else:
                    log = DailyLog(user_id=current_user.id, date=today,
                                   strength_rating=rating, completion=completion, note=note)
                    db.session.add(log)
                    flash('Daily log saved!', 'success')

                db.session.commit()
            except:
                flash('Something went wrong. Try again.', 'error')
            return redirect(url_for('main.daily_log'))

    # GET — build page data
    today     = date.today()
    today_log = DailyLog.query.filter_by(user_id=current_user.id, date=today).first()

    # Last 7 days history
    week_ago  = today - timedelta(days=6)
    week_logs = DailyLog.query.filter(
        DailyLog.user_id == current_user.id,
        DailyLog.date >= week_ago
    ).order_by(DailyLog.date.desc()).all()

    # Pattern analysis — last 30 days
    month_ago   = today - timedelta(days=30)
    month_logs  = DailyLog.query.filter(
        DailyLog.user_id == current_user.id,
        DailyLog.date >= month_ago,
        DailyLog.strength_rating != None
    ).all()

    # Weakest day of week
    day_ratings = defaultdict(list)
    for log in month_logs:
        day_ratings[log.date.strftime('%A')].append(log.strength_rating)
    day_avgs = {day: round(sum(r)/len(r), 1) for day, r in day_ratings.items()}
    weakest_day = min(day_avgs, key=day_avgs.get) if day_avgs else None
    strongest_day = max(day_avgs, key=day_avgs.get) if day_avgs else None

    # Completion rate
    completion_rate = None
    if month_logs:
        full_count  = sum(1 for l in month_logs if l.completion == 'full')
        completion_rate = round((full_count / len(month_logs)) * 100)

    # Today's workout focus based on split
    workout_focus = get_workout_focus(current_user.split_pref, today)

    return render_template('daily_log.html',
        user=current_user,
        today=today,
        today_log=today_log,
        week_logs=week_logs,
        weakest_day=weakest_day,
        strongest_day=strongest_day,
        completion_rate=completion_rate,
        workout_focus=workout_focus,
        day_avgs=day_avgs,
    )

# ── Workout focus logic ───────────────────────────────────────────────────────
def get_workout_focus(split_pref, today):
    if not split_pref:
        return None

    bro_split = ['Chest', 'Back', 'Shoulders', 'Arms', 'Legs', 'Rest', 'Rest']
    ppl_split = ['Push', 'Pull', 'Legs', 'Push', 'Pull', 'Legs', 'Rest']

    bro_exercises = {
        'Chest':     [('Bench Press', '4', '6–8'), ('Incline DB Press', '3', '10'), ('Cable Flyes', '3', '12'), ('Dips', '3', '10')],
        'Back':      [('Deadlift', '4', '5'), ('Barbell Row', '4', '8'), ('Pull-ups', '3', '8–10'), ('Lat Pulldown', '3', '12')],
        'Shoulders': [('Overhead Press', '4', '8'), ('Lateral Raises', '4', '15'), ('Face Pulls', '3', '15'), ('Arnold Press', '3', '10')],
        'Arms':      [('Barbell Curl', '4', '10'), ('Hammer Curl', '3', '12'), ('Close-Grip Bench', '4', '10'), ('Skull Crushers', '3', '12')],
        'Legs':      [('Squat', '4', '6–8'), ('Romanian Deadlift', '3', '10'), ('Leg Press', '3', '12'), ('Calf Raises', '4', '20')],
    }
    ppl_exercises = {
        'Push': [('Bench Press', '4', '8'), ('Overhead Press', '3', '8'), ('Lateral Raises', '4', '15'), ('Tricep Pushdown', '3', '12')],
        'Pull': [('Deadlift', '4', '5'), ('Pull-ups', '3', '10'), ('Barbell Row', '3', '8'), ('Barbell Curl', '3', '12')],
        'Legs': [('Squat', '4', '8'), ('Romanian Deadlift', '3', '10'), ('Leg Press', '3', '12'), ('Calf Raises', '4', '20')],
    }

    day_index = today.weekday()  # Mon=0, Sun=6
    if split_pref == 'bro':
        focus = bro_split[day_index]
        exercises = bro_exercises.get(focus, [])
    else:
        focus = ppl_split[day_index]
        exercises = ppl_exercises.get(focus, [])

    return { 'focus': focus, 'exercises': exercises, 'is_rest': focus == 'Rest' }

# ── Chatbot page ─────────────────────────────────────────────────────────────
@main.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html', user=current_user)

# ── Chatbot API ──────────────────────────────────────────────────────────────
@main.route('/chatbot/message', methods=['POST'])
@login_required
def chatbot_message():
    from app.chatbot import get_response
    data    = request.get_json()
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'reply': "I didn't catch that. Try asking something about fitness!"})
    reply = get_response(message, current_user)
    return jsonify({'reply': reply})
