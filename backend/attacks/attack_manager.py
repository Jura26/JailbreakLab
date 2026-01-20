# Centralized attack handling

from attacks.rolePlaying import run_role_playing_attack
from attacks.chainOfQuestions import run_chain_of_questions_attack
from attacks.asciiArtJailbreak import run_ascii_art_jailbreak_attack
from attacks.FCB import run_fcb_attack
from attacks.neuroStrike.neuroStrike import run_neurostrike_attack
from attacks.GCG import run_gcg_attack
from attacks.danAttack import run_dan_attackJailbreak
from attacks.DAN6 import run_dan_attack6
from attacks.DAN9 import run_dan_attack9
from attacks.DAN11 import run_dan_attack11
from attacks.stanAttack import run_stan_attack
from attacks.mongoTom import run_mongoTom_attack
from attacks.TAP import run_tap_attack
from attacks.PAIR_attack.main import run_PAIR_attack
from attacks.base64_encoded import run_base64_attack
from attacks.base64_with_competing import run_base64_competing_attack
from attacks.ubbi_dubbi import run_ubbi_dubbi_attack
from attacks.rot13_encoded import run_rot13_attack
from attacks.leetspeak_attack import run_leetspeak_attack
from attacks.aigy_paigy_attack import run_aigy_paigy_attack
from attacks.Crescendo.crescendo import run_crescendo
from attacks.poem_attack import run_poem_attack

def run_attack(attack_type, model_id, template, defense, session_id):
    """
    Runs the specified attack and returns the generator.
    Returns None if attack_type is not recognized.
    """
    if attack_type == "role-playing-social-engeneering":
        return run_role_playing_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "chain-of-questions":
        return run_chain_of_questions_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "DANJailbreak":
        return run_dan_attackJailbreak(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "DAN6":
        return run_dan_attack6(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "DAN9":
        return run_dan_attack9(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "DAN11":
        return run_dan_attack11(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "stan":
        return run_stan_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "mongoTom":
        return run_mongoTom_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "ascii-art-jailbreak":
        return run_ascii_art_jailbreak_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "neurostrike":
        return run_neurostrike_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "fcb-bias_guided":
        return run_fcb_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "gcg-gradient":
        return run_gcg_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "tap-tree_pruning":
        return run_tap_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type =="PAIR_attack":
        return run_PAIR_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "base64-attack":
        return run_base64_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "base64-competing-attack":
        return run_base64_competing_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "ubbi-dubbi-attack":
        return run_ubbi_dubbi_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "rot13-attack":
        return run_rot13_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "leetspeak-attack":
        return run_leetspeak_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "aigy-paigy-attack":
        return run_aigy_paigy_attack(
            model_id=model_id,
            template=template,
            defense=defense,
            session_id=session_id
        )
    elif attack_type == "crescendo":
        return run_crescendo(model_id=model_id,
        template=template,
        defense=defense,
        session_id=session_id
        )
    elif attack_type == "poem_attack":
        return run_poem_attack(model_id=model_id,
        template=template,
        defense=defense,
        session_id=session_id
        )
    else:
        return None