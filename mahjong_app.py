from flask import Flask, render_template, request

app = Flask(__name__)

# 基本的な役と点数
YAKU = {
    'リーチ': 1,
    '断幺九': 1,
    '平和': 1,
    '一杯口': 1,
    '三色同順': 2,
    '対々和': 2,
    '三暗刻': 2,
    '小三元': 2,
    '混一色': 3,
    '清一色': 6,
    '大三元': 13,
    '四暗刻': 13,
    '字一色': 13,
    '清老頭': 13,
    '四喜和': 13,
    '天和': 13,
    '地和': 13,
    '九蓮宝燈': 13,
    '緑一色': 13,
    '大四喜': 13,
    '四暗刻単騎': 13,
    '純正九蓮宝燈': 13,
}

# 符計算
def calculate_fu(hand_type, wait_type, pair_type, mentsu_list):
    fu = 20  # 基本符
    
    # 和了方法による符
    if hand_type == 'ロン':
        fu += 10
    elif hand_type == 'ツモ':
        fu += 2
    
    # 待ちによる符
    if wait_type == '両面待ち':
        fu += 0
    elif wait_type == '辺張待ち':
        fu += 2
    elif wait_type == '嵌張待ち':
        fu += 2
    elif wait_type == '単騎待ち':
        fu += 2
    elif wait_type == '双ポン待ち':
        fu += 0
    
    # 対子による符
    if pair_type == '役牌':
        fu += 2
    
    # 面子による符
    for mentsu in mentsu_list:
        if mentsu['type'] == '暗刻':
            if mentsu['tile'] in ['1', '9'] or mentsu['tile'] in ['東', '南', '西', '北', '白', '發', '中']:
                fu += 8
            else:
                fu += 4
        elif mentsu['type'] == '明刻':
            if mentsu['tile'] in ['1', '9'] or mentsu['tile'] in ['東', '南', '西', '北', '白', '發', '中']:
                fu += 4
            else:
                fu += 2
        elif mentsu['type'] == '暗槓':
            if mentsu['tile'] in ['1', '9'] or mentsu['tile'] in ['東', '南', '西', '北', '白', '發', '中']:
                fu += 32
            else:
                fu += 16
        elif mentsu['type'] == '明槓':
            if mentsu['tile'] in ['1', '9'] or mentsu['tile'] in ['東', '南', '西', '北', '白', '發', '中']:
                fu += 16
            else:
                fu += 8
    
    # 10の倍数に切り上げ
    fu = ((fu + 9) // 10) * 10
    return fu

# 点数計算
def calculate_score(han, fu, is_oya, is_ron):
    if han >= 13:
        # 役満
        if is_oya:
            return 48000 if is_ron else 16000
        else:
            return 32000 if is_ron else 8000
    elif han >= 11:
        # 三倍満
        if is_oya:
            return 36000 if is_ron else 12000
        else:
            return 24000 if is_ron else 6000
    elif han >= 8:
        # 倍満
        if is_oya:
            return 24000 if is_ron else 8000
        else:
            return 16000 if is_ron else 4000
    elif han >= 6:
        # 跳満
        if is_oya:
            return 18000 if is_ron else 6000
        else:
            return 12000 if is_ron else 3000
    else:
        # 通常の点数計算
        base_score = fu * (2 ** (han + 2))
        if is_oya:
            return min(base_score * 6, 12000) if is_ron else min(base_score * 2, 4000)
        else:
            return min(base_score * 4, 8000) if is_ron else min(base_score, 2000)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    selected_yaku = []
    calculated_fu = None
    
    if request.method == 'POST':
        try:
            # 基本情報
            han = int(request.form.get('han', 0))
            fu_input = request.form.get('fu', '')
            is_oya = request.form.get('is_oya') == 'on'
            is_ron = request.form.get('is_ron') == 'on'
            
            # 符計算の入力
            hand_type = request.form.get('hand_type', 'ツモ')
            wait_type = request.form.get('wait_type', '両面待ち')
            pair_type = request.form.get('pair_type', '通常')
            
            # 面子の情報
            mentsu_list = []
            for i in range(4):  # 最大4面子
                mentsu_type = request.form.get(f'mentsu_type_{i}', '')
                mentsu_tile = request.form.get(f'mentsu_tile_{i}', '')
                if mentsu_type and mentsu_tile:
                    mentsu_list.append({
                        'type': mentsu_type,
                        'tile': mentsu_tile
                    })
            
            # 符を計算
            if mentsu_list:
                calculated_fu = calculate_fu(hand_type, wait_type, pair_type, mentsu_list)
                fu = calculated_fu
            elif fu_input:
                fu = int(fu_input)
            else:
                fu = 30  # デフォルト値
            
            # 選択された役
            selected_yaku = request.form.getlist('yaku')
            
            # 役による翻数計算
            yaku_han = sum(YAKU[yaku] for yaku in selected_yaku)
            total_han = han + yaku_han
            
            if total_han > 0:
                score = calculate_score(total_han, fu, is_oya, is_ron)
                result = {
                    'han': total_han,
                    'fu': fu,
                    'score': score,
                    'yaku_list': selected_yaku,
                    'is_oya': is_oya,
                    'is_ron': is_ron,
                    'calculated_fu': calculated_fu
                }
            else:
                error = '翻数が0以下です。役を選択するか翻数を入力してください。'
                
        except (ValueError, KeyError) as e:
            error = f'入力エラー: {str(e)}'
    
    return render_template('mahjong.html', yaku=YAKU, result=result, error=error, selected_yaku=selected_yaku)

@app.route('/fu_help')
def fu_help():
    return render_template('fu_help.html')

@app.route('/han_help')
def han_help():
    return render_template('han_help.html')

@app.route('/fu_manual_help')
def fu_manual_help():
    return render_template('fu_manual_help.html')

@app.route('/yaku_help')
def yaku_help():
    return render_template('yaku_help.html')

if __name__ == '__main__':
    app.run(debug=True)