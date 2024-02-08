function proficiency() {
    return parseInt(document.getElementById('proficiency_bonus').innerHTML);
}

function bonus(stat) {
    return parseInt(document.getElementById(stat + '_bonus').innerHTML);
}

function setStatBonus(stat) {
    var score = document.getElementById(stat).value;
    var bonus = Math.floor((score - 10) / 2);
    document.getElementById(stat + '_bonus').innerHTML = bonus;
}

function setProficiencyBonus() {
    var score = document.getElementById('level').value;
    var bonus = Math.ceil(1 + (0.25 * score));
    document.getElementById('proficiency_bonus').innerHTML = bonus;
}

function setSpellSaveDC() {
    var score = 8 + proficiency() + bonus('wis');
    document.getElementById('spell_save_dc').innerHTML = score;
}

(function () {
    const stats = ['str', 'dex', 'con', 'int', 'wis', 'cha'];
    stats.forEach(setStatBonus);
    setProficiencyBonus();
    setSpellSaveDC();
})();
