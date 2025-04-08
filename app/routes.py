from flask import render_template, request, redirect, url_for, flash, get_flashed_messages
from .utils import *


def render_agents_page(**kwargs):
    base_vars = {
        'agents': AgentsDb.query.all(),
        'show_add_agent': False,
        'show_edit_agent': False,
        'show_delete_agent': False,
        'show_clear_db': False,
        'id_found': False,
        'agent_id': '',
        'errors': {},
        'agent': None,
        'nickname': '',
        'phone': '',
        'email': '',
        'access_level': ''
    }
    base_vars.update(kwargs)
    return render_template('agents.html', **base_vars)


@app.route('/')
def agents():
    return render_agents_page()


@app.route('/add-agent', methods=['GET', 'POST'])
def add_agent():
    if request.method == 'GET':
        return render_agents_page(show_add_agent=True)
    else:
        errors = {}
        nickname = request.form.get('agent-nickname').strip().lower()
        phone = request.form.get('agent-phone').strip()
        email = request.form.get('agent-email').strip().lower()
        access_level = request.form.get('agent-access-level').strip().lower()

        if not verify_nickname(nickname):
            errors['nickname'] = 'Никнейм должен включать только буквы и быть уникальным'

        if not verify_phone(phone):
            errors['phone'] = 'Неверный формат номера'

        if not verify_email(email):
            errors['email'] = 'Неверный формат e-mail'

        if errors:
            return render_agents_page(show_add_agent=True,
                                      errors=errors,
                                      nickname=nickname,
                                      email=email,
                                      phone=phone,
                                      access_level=access_level)

        new_agent = AgentsDb(nickname=nickname,
                             phone=phone,
                             email=email,
                             access_level=access_level)
        db.session.add(new_agent)
        db.session.commit()
        flash(f'Запись об агенте {nickname} успешно добавлена в базу данных', 'success')

        return redirect(url_for('agents', show_add_agent=False))


@app.route('/generate-nickname', methods=['GET', 'POST'])
def generate_nickname():
    errors = {}

    phone = request.args.get('phone', '')
    email = request.args.get('email', '')
    access_level = request.args.get('access_level', '')

    generated_nickname = get_nickname()
    if not generated_nickname:
        errors['nickname'] = 'Не удалось сгенерировать никнейм'
        return render_agents_page(
            show_add_agent=True,
            phone=phone,
            email=email,
            access_level=access_level,
            errors=errors
        )
    return render_agents_page(
        show_add_agent=True,
        nickname=generated_nickname,
        phone=phone,
        email=email,
        access_level=access_level
    )


@app.route('/edit-agent', methods=['GET'])
def edit_agent():
    agent_id = request.args.get('agent-id')

    if agent_id:
        try:
            agent_id = int(agent_id)
            agent = get_agent_by_id(agent_id)
            if not agent:
                return render_agents_page(show_edit_agent=True,
                                          errors={'id': f'Агент с id {agent_id} не найден'})
        except ValueError:
            return render_agents_page(show_edit_agent=True, errors={'id': 'ID должно быть целым числом'})

        return redirect(url_for('update_agent', agent_id=agent_id))

    return render_agents_page(show_edit_agent=True, id_found=False)


@app.route('/edit-agent/<int:agent_id>', methods=['GET', 'POST'])
def update_agent(agent_id):
    agent = get_agent_by_id(agent_id)

    if request.method == 'POST':
        errors = {}
        changes = {}
        current_nickname = agent.nickname
        nickname = request.form.get('nickname-edit').strip().lower()
        phone = request.form.get('phone-edit').strip()
        email = request.form.get('email-edit').strip().lower()
        access_level = request.form.get('access-level-edit').strip().lower()

        if not verify_nickname(nickname) and nickname != current_nickname:
            errors['nickname'] = 'Никнейм должен включать только буквы и быть уникальным'
        elif verify_nickname(nickname) and nickname != current_nickname:
            changes['никнейм'] = True

        if not verify_phone(phone):
            errors['phone'] = 'Неверный формат номера'
        else:
            if phone != agent.phone:
                changes['телефон'] = True

        if not verify_email(email):
            errors['email'] = 'Неверный формат e-mail'
        else:
            if email != agent.email:
                changes['e-mail'] = True

        if access_level != agent.access_level:
            changes['уровень доступа'] = True

        if errors:
            return render_agents_page(show_edit_agent=True,
                                      id_found=True,
                                      agent_id=agent_id,
                                      errors=errors,
                                      nickname=nickname,
                                      phone=phone,
                                      email=email,
                                      access_level=access_level)
        if changes:
            if changes.get('никнейм'):
                agent.nickname = nickname
            if changes.get('телефон'):
                agent.phone = phone
            if changes.get('e-mail'):
                agent.email = email
            if changes.get('уровень доступа'):
                agent.access_level = access_level
            db.session.commit()

        if len(changes) == 1:
            flash(f'Запись об агенте с id {agent.id} успешно обновлена, изменено поле: {'/'.join([key for key in changes.keys()])}',
                  'success')
        elif len(changes) > 1:
            flash(
                f'Запись об агенте с id {agent.id} успешно обновлена, изменены поля: {'/'.join([key for key in changes.keys()])}',
                'success')

        return redirect(url_for('agents', show_edit_agent=False))

    return render_agents_page(show_edit_agent=True,
                              id_found=True,
                              agent_id=agent_id,
                              nickname=agent.nickname,
                              phone=agent.phone,
                              email=agent.email,
                              access_level=agent.access_level)


@app.route('/delete-agent', methods=['GET'])
def delete_agent():
    agent_id = request.args.get('agent-id')

    if agent_id:
        try:
            agent_id = int(agent_id)
            agent = get_agent_by_id(agent_id)
            if not agent:
                return render_agents_page(show_delete_agent=True,
                                          errors={'id': f'Агент с id {agent_id} не найден'})
        except ValueError:
            return render_agents_page(show_delete_agent=True,
                                      errors={'id': 'ID должно быть целым числом'})

        return redirect(url_for('confirm_delete_agent', agent_id=agent_id))

    return render_agents_page(show_delete_agent=True, id_found=False)


@app.route('/delete-agent/<int:agent_id>', methods=['GET', 'POST'])
def confirm_delete_agent(agent_id):
    agent = get_agent_by_id(agent_id)

    if request.method == 'POST':
        agent = get_agent_by_id(agent_id)
        nickname = agent.nickname
        phone = agent.phone
        email = agent.email
        access_level = agent.access_level
        db.session.delete(agent)
        db.session.commit()
        flash(f'Запись об агенте {agent_id} {nickname} успешно удалена', 'success')
        return redirect(url_for('agents',
                                show_delete_agent=False,
                                agent_id=agent_id,
                                nickname=nickname,
                                phone=phone,
                                email=email,
                                access_level=access_level))

    return render_agents_page(show_delete_agent=True,
                              id_found=True,
                              agents=AgentsDb.query.all(),
                              agent_id=agent_id,
                              nickname=agent.nickname,
                              phone=agent.phone,
                              email=agent.email,
                              access_level=agent.access_level)


@app.route('/search-agent', methods=['GET'])
def search_agent():
    nickname = request.args.get('nickname')

    if not nickname:
        return redirect(url_for('agents'))

    agent = AgentsDb.query.filter_by(nickname=nickname.strip().lower()).first()
    if not agent:
        flash(f'Агент с никнеймом "{nickname}" не найден', 'error')

    return render_agents_page(agent=agent)


@app.route('/clear-db', methods=['GET', 'POST'])
def clear_db():
    if request.method == 'GET':
        return render_agents_page(show_clear_db=True)
    AgentsDb.query.delete()
    db.session.commit()
    return render_agents_page()


@app.route('/close-modal')
def close_modal():
    return redirect(url_for('agents',
                            show_add_agent=False,
                            show_edit_agent=False,
                            show_delete_agent=False,
                            show_clear_db=False))