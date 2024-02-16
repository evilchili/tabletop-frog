function getTraitModifiersForStat(stat) {
    var mods = {};
    for (const prop in TRAITS) {
        var props = [];
        for (const desc in TRAITS[prop]) {
            trait = TRAITS[prop][desc]
            if (trait.type == "stat" && trait.target == stat) {
                props.push(trait);
            }
        }
        if (props) {
            mods[prop] = props;
        }
    }
    return mods;
}

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

function applyStatModifiers(stat) {
    var score = parseInt(document.getElementById(stat).value);
    var modsForStat = getTraitModifiersForStat(stat);
    for (desc in modsForStat) {
        for (idx in modsForStat[desc]) {
            var value = modsForStat[desc][idx].value;
            console.log(`Ancestry Trait "${desc}" grants ${value} to ${stat}`);
            score += parseInt(value);
        }
    }
    document.getElementById(stat).value = score;
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
    stats.forEach(applyStatModifiers);
    stats.forEach(setStatBonus);
    setProficiencyBonus();
    // setSpellSaveDC();
    
})();
