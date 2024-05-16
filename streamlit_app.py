import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import requests,json,hashlib,uuid,datetime,pytz
from sdb import dbc
db = dbc(un=st.secrets['db_username'],pw=st.secrets['db_token'],host=st.secrets['db_addr'],port=st.secrets['db_port'],db=st.secrets['db_db'])

"""
`///streamlit testing zone///`   `///jank zone///`   `///streamlit testing zone///`
"""
"""
I'm messing with the `streamlit` library because I want to test out their new `st.data_editor` feature in some private code.
"""

def login(email,pw):
    try:
        #st.toast('login called')
        tempc = db.getcbyemail(email)
        loginpop.caption(tempc)
        if tempc and 'salt' in tempc.keys() and loginpw: hash = hashlib.sha512(f"{tempc['salt']}{pw}".encode(encoding="utf-8"),usedforsecurity=True).hexdigest()
        else: hash = None
        if hash: loginpop.caption(hash)
        if hash and loginpop.button(label='check pw'): 
            if hash == st.session_state.c['hash']: loginpop.caption('correct pw')
            else: loginpop.caption('incorrect pw')
        if hash == tempc['hash']:
            loginpop.caption('hashes mashes')
            st.session_state.seshdata = db.getsesh(tempc['id'])
            if not st.session_state.seshdata: st.session_state.seshdata = db.addsesh(st.session_state.c['id'])
            loginpop.caption(str(st.session_state.seshdata))
            st.session_state.c = tempc
        tempc = None
        if st.session_state.seshdata: st.toast(f"logged in with {st.session_state.seshdata['id']}")
        return
    except Exception as e:
        st.toast(str(e))

def startup():
    if 'seshdata' not in st.session_state:
        st.session_state.seshdata = None
    if 'c' not in st.session_state:
        st.session_state.c = None
    #st.caption(f"sd {st.session_state.seshdata}")
    #st.caption(body=f"c {st.session_state.c}")
    if st.session_state.seshdata:
        st.session_state.c = db.getcontact(st.session_state.seshdata['cid'])
        #if datetime.datetime.now() > datetime.datetime.strptime(st.session_state.seshdata['exp'],'%Y-%m-%dT%H:%M:%S+00:00'):
        #    st.session_state.seshdata = None
        #    st.session_state.c = None
startup()

if st.session_state.seshdata is None:
    signpop = st.sidebar.expander('create acct')
    nfn = signpop.text_input('fn')
    nln = signpop.text_input('ln')
    nphone = signpop.text_input('phone')
    nemail = signpop.text_input('email*')
    npw = signpop.text_input('pw*',type='password')
    vpw = signpop.text_input('verify*',type='password')
    nsalt = str(uuid.uuid4())
    if npw and npw != '' and npw == vpw: nhash = hashlib.sha512(f"{nsalt}{npw}".encode(encoding="utf-8"),usedforsecurity=True).hexdigest()
    else: nhash = None
    if nhash and signpop.button('register'):
        st.session_state.seshdata = db.addcontact(email=nemail,phone=nphone,fn=nfn,ln=nln,salt=nsalt,hash=nhash)
        st.session_state.c = db.getcbyemail(nemail)
        nfn,nln,nphone,nemail,npw,vpw,nsalt = '','','','','','',''

if st.session_state.seshdata is None:
    loginpop = st.sidebar.expander('login')
    loginemail = loginpop.text_input(label='email',value='',max_chars=50,type='default')
    loginpw = loginpop.text_input(label='pw',value='',max_chars=50,type='password')
    if loginemail != '': c = db.getcbyemail(loginemail)
    if loginpop.button('login'): 
        login(loginemail,loginpw)
    #st.caption(f"sesh: {str(seshdata)}")
    worked = None
    #q = st.caption(f"worked: {str(worked)}")

if st.session_state.seshdata:
    st.sidebar.caption(f"logged in as {st.session_state.c['email']}")
    if st.sidebar.button('logout'):
        db.delsesh(st.session_state.seshdata)
        st.session_state.seshdata = None
    chpw = st.sidebar.expander('change pw')
    npw = chpw.text_input('new pw',type='password')
    if npw != '' and st.session_state.c and 'salt' in st.session_state.c.keys() and st.session_state.c['salt'] != '' and chpw.button('update'):
        chash = hashlib.sha512(f"{st.session_state.c['salt']}{npw}".encode(encoding="utf-8"),usedforsecurity=True).hexdigest()
        db.updatehash(cid=st.session_state.c['cid'],hash=chash)
        st.session_state.c['salt'] = chash
        chpw.caption(f"current hash {st.session_state.c['hash']}")
        chpw.caption(f"new hash {chash}")
        st.toast('pw updated')
    st.link_button('DL my resume',url='https://hartzell.io/resume')
    fwd = db.fwrept()
    #st.caption(fwd)
    fwf = pd.DataFrame(fwd)
    #st.caption(fwf)
    edits = st.data_editor(fwf.copy(),use_container_width=True,num_rows='dynamic',column_config={'id':None,'asdf':'shit for fucking with crud actions in streamlit'})
    rows = fwf.to_dict('records')
    st.caption(f'rows {rows}')
    rows2 = edits.to_dict('records')
    st.caption(f'rows2 {rows2}')
    if st.button('save shit'):
        for row in rows:
            if row not in rows2: 
                db.fwdel(row['id'])
            else:
                for row2 in rows2:
                    if row['id'] == row2['id'] and row['asdf'] != row2['asdf']:
                        db.fwup(row2['id'],row2['asdf'])
        for row2 in rows2:
            if row2 not in rows: db.fwadd(row2['asdf'])
    delpop = st.sidebar.expander('delete account')
    if st.session_state.seshdata and delpop.button('really delete account'):
        worked = db.delcontact(st.session_state.seshdata['cid'])
        st.caption(str(worked))
        if worked: 
            st.toast('account deleted')
            st.caption('deleted')
            st.session_state.seshdata = None
        else: 
            st.toast('failed to delete acct')
            st.caption('not deleted')

st.sidebar.caption(f"sesh {st.session_state.seshdata}")
st.sidebar.caption(f"c {st.session_state.c}")

"""
`///streamlit testing zone///`   `///jank zone///`   `///streamlit testing zone///`
"""

defautgraph = st.expander('default graph')
defautgraph.caption('I could not bring myself to delete this from the template. Also 669 points & 114 turns looks pretty cool btw')
num_points = defautgraph.slider("Number of points in spiral", 1, 10000, 1100)
num_turns = defautgraph.slider("Number of turns in spiral", 1, 300, 31)

indices = np.linspace(0, 1, num_points)
theta = 2 * np.pi * num_turns * indices
radius = indices

x = radius * np.cos(theta)
y = radius * np.sin(theta)

df = pd.DataFrame({
    "x": x,
    "y": y,
    "idx": indices,
    "rand": np.random.randn(num_points),
})

defautgraph.altair_chart(alt.Chart(df, height=700, width=700)
    .mark_point(filled=True)
    .encode(
        x=alt.X("x", axis=None),
        y=alt.Y("y", axis=None),
        color=alt.Color("idx", legend=None, scale=alt.Scale()),
        size=alt.Size("rand", legend=None, scale=alt.Scale(range=[1, 150])),
    ))

clist = db.contactrept()
df = pd.DataFrame(clist)
edited = st.data_editor(df,column_config={'id':None,'fn':None,'ln':None},use_container_width=True)