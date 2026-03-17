import re
import random

# ── Intent definitions ────────────────────────────────────────────────────────
# Each intent has: keywords (list of patterns) + responses (pool to pick from randomly)

INTENTS = [

    {
        'name': 'greeting',
        'patterns': [r'\b(hi|hello|hey|sup|what\'s up|wassup|good morning|good evening|good afternoon)\b'],
        'responses': [
            "Hey {name}! 💪 Ready to crush it today? Ask me anything about fitness, diet, or training.",
            "Hello {name}! I'm CONST Bot — your AI fitness coach. What do you want to work on today?",
            "Hey {name}! What's on your mind — workouts, diet, recovery, or something else?",
        ]
    },

    # ── WORKOUT ──────────────────────────────────────────────────────────────
    {
        'name': 'workout_beginner',
        'patterns': [r'\b(beginner|just started|new to gym|start(ing)? (at|the) gym|where do i start|how do i start)\b'],
        'responses': [
            "Great that you're starting {name}! 🏋️ For beginners, focus on the basics first — compound movements like squats, deadlifts, bench press, rows, and overhead press. These hit multiple muscle groups and build a strong foundation. Start with 3 days/week full body, learn the form before adding weight.",
            "Welcome to the journey {name}! Don't overthink it early on. Pick a simple 3-day program — push/pull/legs or full body. Focus on progressive overload: add a little weight or reps every week. Consistency for 3 months beats any fancy program.",
            "Starting out? Keep it simple {name}. Gym 3x a week, compound movements, eat enough protein (around 1.6g per kg of bodyweight), sleep 7–8 hours. That formula alone will get you significant results in 3 months.",
        ]
    },

    {
        'name': 'workout_split',
        'patterns': [r'\b(bro split|push pull|ppl|split|workout split|training split|which split)\b'],
        'responses': [
            "Both Bro Split and PPL work great {name}. PPL (Push/Pull/Legs) is more efficient — each muscle gets hit twice a week which is optimal for hypertrophy. Bro split works too but muscles only get hit once. If you can train 5–6 days, PPL wins. 3–4 days? Full body or Upper/Lower.",
            "For natural lifters, frequency matters {name}. PPL hits each muscle 2x/week which is better for muscle protein synthesis. Bro split hits once — fine for beginners but suboptimal long term. That said, the best split is one you actually stick to.",
            "Bro split vs PPL — PPL wins on paper for most people {name}. But honestly? The split matters less than consistency, progressive overload, and sleep. Pick one and run it for 12 weeks minimum before judging.",
        ]
    },

    {
        'name': 'workout_progressive_overload',
        'patterns': [r'\b(progressive overload|getting stronger|add weight|increase weight|strength gain|how to progress)\b'],
        'responses': [
            "Progressive overload is THE principle of training {name}. Simply put — do more over time. Add weight, add reps, add sets, or reduce rest time. Even 0.5kg more per week adds up to 26kg stronger in a year. Track your lifts so you know what to beat.",
            "The secret to gains is simple {name} — progressive overload. Every session, try to do a little more than last time. Can't add weight? Add one more rep. Can't do that? Add one more set. Progression is the stimulus for growth.",
            "Progressive overload is non-negotiable {name}. Your muscles adapt to stress — give them the same stress every week and they stop growing. Make a log, track every session, and aim to beat your numbers weekly.",
        ]
    },

    {
        'name': 'workout_chest',
        'patterns': [r'\b(chest|bench press|pecs|chest day|chest workout|chest exercise)\b'],
        'responses': [
            "For chest {name} — the big 3 are: flat bench press (overall mass), incline press (upper chest), and cable flyes (isolation). Most people neglect upper chest — fix that with incline work. Aim for 12–20 sets per week spread across 2 sessions.",
            "Best chest exercises {name}: Barbell bench press for strength, incline dumbbell press for upper chest, cable flyes for stretch and contraction, dips for lower chest. Hit chest 2x a week for best results.",
            "Chest tip {name}: Most people bench too heavy with bad form. Go slightly lighter, slow the eccentric (lowering phase to 3 seconds), feel the pecs working. Better mind-muscle connection = better growth.",
        ]
    },

    {
        'name': 'workout_back',
        'patterns': [r'\b(back|deadlift|pull up|lat|rows|back workout|back exercise|lats|rhomboid)\b'],
        'responses': [
            "Back is the most important muscle group for posture and injury prevention {name}. Focus on: deadlifts (overall thickness), pull-ups (lat width), barbell rows (mid-back), face pulls (rear delts/rotator cuff). Train back with as much intensity as chest.",
            "For a wide back {name}: Pull-ups and lat pulldowns build width. Rows (barbell, dumbbell, cable) build thickness. Deadlifts build overall back strength. Most people overtrain chest and undertrain back — balance it out.",
            "Back tip {name}: Learn to feel your lats. Before pulling movements, depress and retract your shoulder blades first. This ensures you're actually using your back, not just your arms.",
        ]
    },

    {
        'name': 'workout_legs',
        'patterns': [r'\b(leg|squat|legs day|quad|hamstring|glute|calf|leg workout|skip leg)\b'],
        'responses': [
            "Never skip legs {name}! 🦵 Legs are half your body. Squats are king — they build quad, glute, and overall body strength. Add Romanian deadlifts for hamstrings, leg press for volume, calf raises. Leg day releases the most testosterone and growth hormone of any workout.",
            "Leg day essentials {name}: Squat (compound king), Romanian deadlift (hamstrings), leg press (quad volume), leg curl (hamstring isolation), calf raises. Don't rush leg day — it's the hardest but most rewarding session.",
            "Legs tip {name}: Most people squat too high — go to at least parallel for full quad and glute development. Also, calves need HIGH volume (15–20+ reps) because they're stubborn muscles used to constant activity.",
        ]
    },

    {
        'name': 'workout_cardio',
        'patterns': [r'\b(cardio|running|treadmill|cycling|hiit|aerobic|fat burn|burn fat|cardio workout)\b'],
        'responses': [
            "Cardio is a tool {name}, not a punishment. For fat loss, a calorie deficit beats cardio alone. But cardio improves heart health, recovery, and helps create a deficit. 2–3x/week of 20–30 min moderate cardio is plenty for most people. Don't overdo it — it can eat into recovery.",
            "HIIT vs steady state {name}: HIIT burns more calories in less time and has an afterburn effect. Steady state is easier to recover from and good for active recovery. For fat loss, both work — pick what you'll actually do consistently.",
            "Don't fear cardio {name} but don't rely on it either. You can't out-run a bad diet. Sort the nutrition first, then use cardio as a tool to accelerate fat loss or improve fitness. 150 min/week of moderate activity is the baseline for health.",
        ]
    },

    {
        'name': 'workout_arms',
        'patterns': [r'\b(arm|bicep|tricep|curl|arms workout|arm day|big arms)\b'],
        'responses': [
            "Big arms = big triceps {name}. Triceps are 2/3 of your upper arm. Best movements: close-grip bench, skull crushers, overhead tricep extension. For biceps: barbell curl (mass), incline dumbbell curl (stretch), hammer curl (brachialis). Train arms 2x/week.",
            "Arm tips {name}: Don't just curl — focus on the full range of motion. For biceps, fully extend at the bottom and squeeze at the top. For triceps, overhead extension gives the best stretch. Ego lifting with bad form = no gains.",
            "Arms grow from compound movements too {name}. Your biceps get hit on all pulling exercises, triceps on all pushing. Isolation work is just the finisher. If your arms aren't growing, increase your back and chest volume first.",
        ]
    },

    # ── DIET & NUTRITION ─────────────────────────────────────────────────────
    {
        'name': 'diet_protein',
        'patterns': [r'\b(protein|how much protein|protein intake|high protein|protein source|protein goal)\b'],
        'responses': [
            "For muscle building {name}, aim for 1.6–2.2g of protein per kg of bodyweight. So if you're 70kg, that's 112–154g/day. Best sources: chicken, fish, eggs, paneer, Greek yogurt, lentils, tofu. Spread it across meals — your body can only use so much at once.",
            "Protein is the most important macro for body composition {name}. It builds muscle, keeps you full, and has the highest thermic effect (burns more calories digesting it). Hit your protein goal first, then fill carbs and fats around it.",
            "Good protein sources {name}: Chicken breast (31g/100g), eggs (6g each), paneer (18g/100g), Greek yogurt (10g/100g), dal/lentils (9g/100g cooked), tofu (8g/100g). If you struggle to hit protein from food, whey protein is a convenient supplement.",
        ]
    },

    {
        'name': 'diet_bulk',
        'patterns': [r'\b(bulk|bulking|gain (weight|muscle|mass)|muscle gain|eat more|caloric surplus|surplus)\b'],
        'responses': [
            "For bulking {name}, eat 300–500 calories above your maintenance. More than that and you gain excess fat. Focus on protein (2g/kg), complex carbs (rice, oats, chapati), and healthy fats (nuts, eggs, avocado). Train heavy and sleep 8 hours.",
            "Bulking tip {name}: Most people eat too little and wonder why they're not growing. Use a calorie tracker for 2 weeks to see where you actually are. If the scale isn't going up 0.25–0.5kg/week, eat more.",
            "Clean bulk vs dirty bulk {name}: Clean bulk (small surplus, quality food) keeps fat gain minimal but is slower. Dirty bulk (eat everything) adds mass faster but also fat. For most people, a clean bulk at 300–400 cal surplus is the sweet spot.",
        ]
    },

    {
        'name': 'diet_cut',
        'patterns': [r'\b(cut|cutting|lose (weight|fat)|fat loss|caloric deficit|deficit|lean out|shred)\b'],
        'responses': [
            "For cutting {name}, eat 300–500 calories below maintenance. Keep protein HIGH (2–2.5g/kg) to preserve muscle. Reduce carbs and fats. Don't crash diet — losing more than 0.7kg/week means you're losing muscle too.",
            "Cutting tips {name}: High protein, high fibre foods keep you full on fewer calories. Prioritize sleep — poor sleep increases hunger hormones. Keep training intensity high even in a deficit to signal your body to keep muscle.",
            "Fat loss is simple in theory {name}: calories in < calories out. But the trick is doing it without losing muscle. High protein + resistance training + moderate deficit = fat loss while keeping gains. Cardio helps but isn't mandatory.",
        ]
    },

    {
        'name': 'diet_macros',
        'patterns': [r'\b(macro|macros|carb|carbs|fat|fats|calorie|calories|how much to eat|tdee|maintenance)\b'],
        'responses': [
            "Basic macro split for muscle building {name}: Protein 30–35%, Carbs 40–45%, Fats 20–25%. For cutting, shift to Protein 35–40%, Carbs 30–35%, Fats 25–30%. These are starting points — adjust based on how your body responds.",
            "Calories first, macros second {name}. Figure out your maintenance calories (bodyweight in kg × 33 roughly), then add or subtract based on goal. Then hit your protein target. Carbs and fats can be flexible.",
            "Don't fear carbs {name}. Carbs are your primary fuel source for training. Rice, oats, chapati, sweet potato — these are your friends. Only reduce them when cutting, and even then keep some around your workouts.",
        ]
    },

    {
        'name': 'diet_meal_timing',
        'patterns': [r'\b(meal timing|when to eat|pre workout meal|post workout meal|breakfast|eat before|eat after)\b'],
        'responses': [
            "Meal timing matters less than total daily intake {name}, but here's the guideline: eat a mixed meal 1.5–2 hours before training (carbs + protein). Post workout, eat protein within 1–2 hours. Don't train fasted if you're trying to build muscle.",
            "Pre-workout meal {name}: 1–2 hours before — complex carbs + moderate protein. Example: rice + chicken, or oats + eggs, or banana + peanut butter. Post-workout: prioritize protein within 2 hours — your muscles are most receptive.",
            "The post-workout 'anabolic window' is real but not as narrow as people think {name}. You don't need to chug a shake the second you finish your last set. Just eat a proper protein-rich meal within 2 hours and you're good.",
        ]
    },

    {
        'name': 'diet_vegetarian',
        'patterns': [r'\b(vegetarian|veg|vegan|plant.based|no meat|paneer|tofu|dal|lentil)\b'],
        'responses': [
            "Vegetarian gains are 100% possible {name}! Key protein sources: paneer (18g/100g), tofu (8g/100g), Greek yogurt (10g/100g), lentils/dal (9g/100g cooked), chickpeas (9g/100g), eggs if you eat them. Combine multiple sources to get complete amino acids.",
            "Building muscle on veg is completely doable {name}. The challenge is hitting high protein targets. Solution: Greek yogurt, paneer, tofu, lentils, chickpeas, and whey protein if needed. Eat a variety of plant proteins to cover all amino acids.",
            "Veg protein tip {name}: Combine rice + dal in the same meal — together they form a complete protein (all essential amino acids). Paneer is probably the most versatile high-protein veg food. Greek yogurt as a snack is also excellent.",
        ]
    },

    {
        'name': 'diet_hydration',
        'patterns': [r'\b(water|hydrat|drink water|how much water|thirsty)\b'],
        'responses': [
            "Hydration is underrated {name}. Aim for 3–4 litres of water daily — more on training days. Even mild dehydration (2%) reduces strength and cognitive performance. Drink 500ml first thing in the morning, sip throughout the day, and extra around workouts.",
            "Water tip {name}: If your urine is pale yellow, you're hydrated. Dark yellow = drink more. Clear = you might be overdrinking. Simple. Most people are chronically mildly dehydrated which kills performance.",
            "Hydration affects everything {name} — strength, recovery, skin, digestion, focus. 3–4L/day as a baseline, more in summer or on intense training days. Add electrolytes (a pinch of salt + lemon) if you sweat a lot.",
        ]
    },

    # ── PROGRESS & PLATEAUS ──────────────────────────────────────────────────
    {
        'name': 'plateau',
        'patterns': [r'\b(plateau|stuck|not losing|not gaining|no progress|weight not moving|same weight|stall)\b'],
        'responses': [
            "Plateaus are normal {name} — your body adapts. To break a weight loss plateau: recalculate your calories (your maintenance drops as you lose weight), increase activity slightly, or take a diet break for 1–2 weeks at maintenance to reset hormones.",
            "Strength plateau {name}? Try these: deload week (reduce weight by 40–50% for a week), change rep ranges, change exercises, prioritize sleep and food. Sometimes a plateau just means you need to eat and sleep more.",
            "If your weight has been stuck for 2+ weeks {name}, something needs to change. Either you're eating more than you think (track strictly for a week), or your body has adapted and needs a new stimulus. Small changes compound over time.",
        ]
    },

    {
        'name': 'progress_slow',
        'patterns': [r'\b(slow progress|results|not seeing results|when will i see|how long|takes too long|patience)\b'],
        'responses': [
            "Real talk {name}: natural muscle building is slow. 1–2kg of muscle per month is excellent progress for a beginner. 0.5kg/month for intermediate. Most people overestimate what they can do in 3 months and underestimate what they can do in 3 years.",
            "Fitness progress isn't linear {name}. Some weeks you'll look better, some worse (water retention, stress, sleep). Judge by monthly trends, not daily. Take monthly progress photos — the mirror lies day to day.",
            "The first 3 months {name} are mostly neurological — your body learns to recruit muscle fibers better. Visible physical changes start around month 3–4. Don't quit before the results show up.",
        ]
    },

    # ── RECOVERY & REST ──────────────────────────────────────────────────────
    {
        'name': 'recovery_sleep',
        'patterns': [r'\b(sleep|rest|recovery|how much sleep|importance of sleep|tired|fatigue|overtraining)\b'],
        'responses': [
            "Sleep is when you actually build muscle {name}. Most muscle protein synthesis happens during sleep. Aim for 7–9 hours. Poor sleep = higher cortisol, lower testosterone, more hunger, and slower recovery. It's as important as training.",
            "If you're always tired {name}, check these: sleep 7–9 hours, eat enough (especially carbs pre-workout), don't train the same muscle 2 days in a row, and take at least 1–2 rest days per week. Overtraining is real.",
            "Recovery tip {name}: You don't grow in the gym, you grow when you rest. Training is the stimulus, food is the material, sleep is when construction happens. Prioritize all three equally.",
        ]
    },

    {
        'name': 'recovery_soreness',
        'patterns': [r'\b(sore|soreness|doms|muscle pain|aching|stiff|hurt after workout)\b'],
        'responses': [
            "DOMS (delayed onset muscle soreness) is normal {name}, especially when starting new exercises. It peaks 24–48 hours after training. Active recovery helps — light walking, stretching, foam rolling. Don't skip training just because you're sore, but don't train the same muscle until soreness is mostly gone.",
            "Soreness ≠ good workout {name}. As you get more experienced you'll feel less sore but still be making gains. Don't chase soreness as a metric. Chase progressive overload instead.",
            "To reduce soreness {name}: stay hydrated, sleep well, eat enough protein, do a proper cool down after training, and consider foam rolling. Contrast showers (hot then cold) also help. It gets better as your body adapts.",
        ]
    },

    {
        'name': 'recovery_rest_days',
        'patterns': [r'\b(rest day|how many rest days|days off|skip gym|need rest|train every day)\b'],
        'responses': [
            "Rest days are not wasted days {name} — they're growth days. Your muscles repair and grow on rest days, not during training. Most people need 1–2 rest days per week minimum. Active rest (walking, light stretching) is better than complete inactivity.",
            "Signs you need more rest {name}: persistent fatigue, strength going down, mood getting worse, poor sleep, constant soreness. These are overtraining signals. Take 2–3 easy days, eat more, sleep more.",
            "Training 6–7 days a week is fine IF you manage volume and intensity properly {name}. But most beginners and intermediates recover better with 4–5 training days and 2–3 rest/active recovery days.",
        ]
    },

    {
        'name': 'recovery_deload',
        'patterns': [r'\b(deload|deload week|take a break|back off week|reduce training)\b'],
        'responses': [
            "A deload week every 4–8 weeks is smart training {name}. Reduce weight by 40–50%, keep the movements but lower intensity. It allows joints, tendons, and CNS to recover. You'll come back feeling fresher and often hit PRs right after.",
            "Deloads aren't weakness {name} — they're part of the plan. Elite athletes deload regularly. Signs you need one: persistent joint pain, strength declining for 2+ weeks, dreading every session, poor sleep despite rest.",
            "Deload tip {name}: Keep the same exercises and rep ranges but cut the weight by half. Alternatively, do active recovery — yoga, swimming, walking. One week of reduced training won't cost you gains, it'll actually boost them.",
        ]
    },

    # ── MOTIVATION ──────────────────────────────────────────────────────────
    {
        'name': 'motivation_general',
        'patterns': [r'\b(motivat|unmotivated|lazy|don\'t want to|not feeling it|give up|quit|no energy|tired of)\b'],
        'responses': [
            "Don't wait for motivation {name} — it's unreliable. Build discipline instead. Motivation is a feeling that comes and goes. Discipline is showing up even when you don't feel like it. The session you least want to do often becomes the best one.",
            "On low days {name}, just commit to 10 minutes. Tell yourself you'll go to the gym, do the warm up, and if you still want to leave — leave. 9 times out of 10 you'll finish the workout. Starting is the hardest part.",
            "Remember why you started {name}. Write it down somewhere. Bad days are part of the journey — they don't erase the progress you've made. One bad week doesn't undo months of consistency.",
        ]
    },

    {
        'name': 'motivation_consistency',
        'patterns': [r'\b(consistent|consistency|habit|routine|discipline|stay on track|keep going)\b'],
        'responses': [
            "Consistency beats perfection every time {name}. A good workout done consistently for a year beats a perfect program done for 3 weeks. Show up, do the work, repeat. That's 90% of fitness.",
            "Build your training around your life {name}, not the other way around. Can't do 5 days? Do 3 and do them well. Missed a session? Forget it and get the next one. The only truly wasted workout is the one you didn't do.",
            "Habit stacking helps {name} — attach your workout to something you already do. Gym right after work, or first thing in the morning. The less you have to decide, the more consistent you'll be.",
        ]
    },

    # ── SUPPLEMENTS ─────────────────────────────────────────────────────────
    {
        'name': 'supplement_creatine',
        'patterns': [r'\b(creatine|creatine monohydrate)\b'],
        'responses': [
            "Creatine is the most researched supplement in history {name} — and it works. 3–5g daily, any time of day (timing doesn't matter much). It increases strength, power output, and muscle volume (water into muscle cells). Safe for long-term use. No loading phase needed.",
            "Creatine monohydrate is the cheapest, most effective form {name}. Don't buy creatine HCL or other fancy forms — no evidence they're better. Take 5g daily with water. Give it 4–6 weeks to see the full effect as it saturates your muscles.",
            "Creatine won't make you big on its own {name}, but it lets you train harder which leads to more gains over time. You might gain 1–2kg in the first week from water retention in muscles — that's normal and not fat.",
        ]
    },

    {
        'name': 'supplement_protein',
        'patterns': [r'\b(protein powder|whey|protein shake|protein supplement|whey protein|isolate|casein)\b'],
        'responses': [
            "Whey protein is just food in powder form {name} — it's not magic. Use it when you can't hit your protein goal from whole foods. Whey isolate is faster absorbing, whey concentrate is cheaper. For most people, concentrate is fine.",
            "You don't NEED protein powder {name}. It's convenient, not mandatory. If you can hit 1.6–2g protein/kg from chicken, eggs, paneer, dal, yogurt — you don't need it. Use it as a top-up when needed.",
            "Casein protein {name} is slower digesting — good before bed to give your body sustained amino acids overnight. Whey is better post-workout for fast absorption. But honestly, the total daily protein matters more than timing.",
        ]
    },

    {
        'name': 'supplement_preworkout',
        'patterns': [r'\b(pre.?workout|pre workout|caffeine|energy drink|energy before gym|stimulant)\b'],
        'responses': [
            "Pre-workouts mainly work because of caffeine {name}. You can get the same effect from a strong coffee 30–45 min before training. Most pre-workouts have high caffeine + some beta-alanine (causes the tingle). Don't become dependent — cycle off every 6–8 weeks.",
            "Pre-workout tip {name}: If you rely on pre-workout to train, fix your sleep and diet first. Those are the real energy sources. Pre-workout is a tool, not a crutch. Also avoid it after 4 PM if you want to sleep well.",
            "Natural pre-workout stack {name}: Black coffee + banana 30–45 min before training. Cheap, effective, no crash. Save the expensive pre-workouts for when you really need the extra push.",
        ]
    },

    {
        'name': 'supplement_general',
        'patterns': [r'\b(supplement|vitamin|omega|multivitamin|fish oil|vitamin d|zinc|magnesium)\b'],
        'responses': [
            "The supplement priority list {name}: 1) Creatine (proven), 2) Protein powder if needed (convenient), 3) Vitamin D if you don't get sun, 4) Omega-3 fish oil (anti-inflammatory, heart health), 5) Magnesium (sleep quality). Everything else is mostly marketing.",
            "Most supplements are a waste of money {name}. The basics that actually have evidence: creatine, vitamin D (if deficient), omega-3, caffeine. Sort your training, diet, and sleep first — those give 95% of results. Supplements are the remaining 5%.",
            "Vitamin D is worth taking {name} especially in India where many people are deficient despite the sun (because we avoid direct sun). 2000–4000 IU daily is a common recommendation. Magnesium glycinate before bed improves sleep quality.",
        ]
    },

    # ── INJURY PREVENTION ────────────────────────────────────────────────────
    {
        'name': 'injury',
        'patterns': [r'\b(injury|injured|pain|hurt|knee pain|shoulder pain|back pain|wrist pain|form|posture)\b'],
        'responses': [
            "If you have sharp pain during a movement {name}, stop immediately. Dull soreness is normal, sharp pain is not. Don't train through sharp pain — one session isn't worth weeks of recovery. Get it checked if it persists more than a few days.",
            "Most gym injuries come from ego lifting {name} — too much weight, too fast. Fix your form first, then add weight. Video yourself from the side for squats and deadlifts. Most people have no idea what their form actually looks like.",
            "Common injury prevention tips {name}: Always warm up (10 min), don't skip mobility work, don't increase weight more than 5–10% per week, learn proper bracing (core tight for compound lifts), and listen to your body. Prevention beats treatment.",
        ]
    },

    # ── BODY COMPOSITION ────────────────────────────────────────────────────
    {
        'name': 'body_composition',
        'patterns': [r'\b(body (composition|fat|recomp)|fat loss|muscle (loss|gain)|recomposition|body fat percentage|abs)\b'],
        'responses': [
            "Body recomposition (gaining muscle while losing fat) is possible {name} — especially for beginners and people returning after a break. It requires a slight deficit, high protein, and consistent training. Progress is slower than dedicated bulk or cut phases but it's steady.",
            "Abs are made in the kitchen {name}. Everyone has abs — they're just hidden under fat. Lower body fat percentage reveals them. Men typically see abs around 10–12% body fat, women around 16–19%. Training abs helps with strength but diet is what reveals them.",
            "Weight on the scale doesn't tell the full story {name}. You can lose fat and gain muscle simultaneously and the scale barely moves — but you look completely different. Use measurements, progress photos, and how clothes fit alongside scale weight.",
        ]
    },

    # ── CARDIO VS WEIGHTS ────────────────────────────────────────────────────
    {
        'name': 'cardio_vs_weights',
        'patterns': [r'\b(cardio vs weights|weights vs cardio|should i do cardio or weights|cardio or gym|which is better)\b'],
        'responses': [
            "For body composition {name}, weights win. Resistance training builds muscle which raises your metabolic rate — you burn more calories even at rest. Cardio burns calories during the session but little after. Ideally, do both: weights 3–5x/week, cardio 2–3x/week.",
            "Weights change your body shape {name}, cardio mainly changes your endurance and cardiovascular health. If your goal is to look better, prioritize lifting. If your goal is heart health and stamina, cardio is essential. Most people benefit from a mix.",
            "Both have their place {name}. Don't do excessive cardio thinking it'll get you lean faster — it eats into recovery and can reduce muscle mass. 2–3 sessions of 20–30 min moderate cardio alongside your training is the sweet spot for most people.",
        ]
    },

    # ── WARMUP & COOLDOWN ────────────────────────────────────────────────────
    {
        'name': 'warmup',
        'patterns': [r'\b(warm up|warmup|cool down|cooldown|stretch|stretching|mobility)\b'],
        'responses': [
            "Always warm up {name} — it's not optional. 5–10 minutes of light cardio raises core temperature, then do dynamic stretches specific to your workout (leg swings before squats, arm circles before pressing). Reduces injury risk and improves performance.",
            "Warm up tip {name}: Do a few lighter sets of your first exercise before your working sets. This is called 'ramping up' — e.g., squat day: bar × 10, 60kg × 5, 80kg × 3, then your working sets. Much better than jumping straight to heavy weight.",
            "Cool down with static stretching {name} — hold each stretch 30–60 seconds after training. Focus on the muscles you just worked. This improves flexibility over time and reduces next-day soreness. 5–10 minutes is enough.",
        ]
    },

    # ── GYM TIPS ────────────────────────────────────────────────────────────
    {
        'name': 'gym_tips',
        'patterns': [r'\b(gym tip|gym advice|gym etiquette|gym habit|track workout|workout log|training log|how to get better)\b'],
        'responses': [
            "Top gym habits {name}: 1) Track your workouts — write down weights/reps every session. 2) Rest 2–3 min between heavy sets. 3) Put your phone away during sets. 4) Re-rack your weights. 5) Focus on progressive overload, not just going through the motions.",
            "Gym tip {name}: Stop watching others and focus on your own training. Everyone starts somewhere. The guy squatting 150kg was once squatting just the bar. Compare yourself to who you were last month, not others.",
            "The best thing you can do in the gym {name}: show up consistently, track your lifts, add a little more weight each week, eat enough protein, and sleep well. That formula works for everyone regardless of genetics.",
        ]
    },

    # ── THANKS / FAREWELL ────────────────────────────────────────────────────
    {
        'name': 'thanks',
        'patterns': [r'\b(thank|thanks|appreciate|helpful|good bot|nice|great)\b'],
        'responses': [
            "Anytime {name}! Stay consistent and the results will follow. 💪",
            "Happy to help {name}! Now go get that workout in. 🔥",
            "That's what I'm here for {name}! Any other questions? 💬",
        ]
    },

    {
        'name': 'farewell',
        'patterns': [r'\b(bye|goodbye|see you|later|cya|take care)\b'],
        'responses': [
            "Later {name}! Stay strong and stay consistent. 💥",
            "See you {name}! Remember — show up, work hard, repeat. 🏋️",
            "Bye {name}! Go crush that workout. 💪",
        ]
    },
]

# ── Fallback responses ────────────────────────────────────────────────────────
FALLBACKS = [
    "I'm not sure I caught that {name}. Try asking about workouts, diet, supplements, recovery, or motivation!",
    "Hmm, I don't have a great answer for that {name}. Ask me about training, nutrition, sleep, or gym tips!",
    "That's outside my expertise {name}! I know fitness, gym, diet, and recovery well — try me on those topics.",
    "I didn't quite get that {name}. You can ask things like 'how much protein do I need' or 'how to break a plateau'.",
]

# ── Core function ─────────────────────────────────────────────────────────────
def get_response(message, user):
    text = message.lower().strip()
    name = user.name.split()[0]  # First name only

    # Try to match an intent
    for intent in INTENTS:
        for pattern in intent['patterns']:
            if re.search(pattern, text):
                response = random.choice(intent['responses'])
                return response.format(name=name)

    # No match — fallback
    return random.choice(FALLBACKS).format(name=name)
