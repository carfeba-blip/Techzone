import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
import os

st.set_page_config(page_title='Techzone')
st.title('Gestión de inventario')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(BASE_DIR, 'InventarioTechZone.xlsx')

if not os.path.exists(ARCHIVO):
    st.error(f'⚠️ Archivo no encontrado: "{ARCHIVO}"')
    st.stop()  
else:
    try:
        df = pd.read_excel(ARCHIVO, engine='openpyxl')
        st.success(f'✅ Archivo cargado correctamente')
        
        if 'FechaIngreso' in df.columns:
            df['FechaIngreso'] = pd.to_datetime(df['FechaIngreso'])
        
        st.write(df.head())

    except Exception as e:
        st.error(f'Ha ocurrido un error al procesar el archivo: {e}')
        st.stop()

# pregunta 2

df['FechaIngreso']=pd.to_datetime(df['FechaIngreso'])
st.dataframe(df)

# Pregunta 3

categorias=df['Categoria'].unique()
categoria_sel= st.multiselect('Categorias:', list(categorias), placeholder='Selecciona 1 o más categorías')

# Pregunta 4

estados=df['Estado'].unique()
estado_sel= st.selectbox('Estado del equipo:',['Disponible','Agotado','Descontinuado','Critico'])

# Pregunta 5

pre_min,pre_max=st.slider('Rango de precios:',min_value=0, max_value=2000, value=(0,2000))

# pregunta 6

df_filtrado=df.copy() 

busqueda = st.text_input( "Buscar producto:", placeholder="Escribe un nombre o palabra clave" )
if busqueda: 
    df_filtrado = df_filtrado[df_filtrado["Producto"].str.contains(busqueda)] 
if not busqueda: 
    st.dataframe(df.iloc[0:0])
else:
    st.dataframe(df_filtrado)

# pregunta 7

df_filtrado2=df.copy() 
activar_stock = st.checkbox

if activar_stock:
    stock_min = st.number_input( "Stock mínimo:", min_value=0, step=1, value=0 ) 
else: 
    stock_min = None

if estado_sel: 
    df_filtrado2=df_filtrado2[df_filtrado2['Estado']==estado_sel]
if activar_stock and stock_min is not None: 
    df_filtrado2 = df_filtrado2[df_filtrado2["Stock"] >= stock_min] 
if not estado_sel and not busqueda and not activar_stock: 
    st.dataframe(df.iloc[0:0]) 
else: 
    st.dataframe(df_filtrado2)

#pregunta 8

st.header('Registro de nuevos productos')

prod_new=st.text_input('Producto:')
cat_new=st.selectbox('Categoria:',categorias)
precio_new=st.number_input('Precio:',min_value=0)
stock_new=st.number_input('Stock:',min_value=0)
fecha_new=st.date_input('Fecha de ingreso:', value=date.today())

def generar_codigo():
    ahora=datetime.now() + timedelta(microseconds=1)
    fecha= ahora.strftime('%y%m%d')
    tiempo= ahora.strftime('%H%M%S')
    return f'MT-{fecha}-{tiempo}'

if st.button('Registrar producto'):
    errores =[]
    if prod_new.strip()=='':
        errores.append('El nombre del producto no puede estar vacio..')
    if precio_new<=0:
        errores.append('El precio debe ser mayor a 0..')
    if stock_new<=0:
        errores.append( 'El stock debe ser mayor o igual a 0..')
    if fecha_new > date.today():
        errores.append('La fecha no puede ser futura..')

    if errores: 
        st.error(' | '.join(errores))
    else:
        nuevo_codigo= generar_codigo()
        nuevo_producto={
            'Codigo': nuevo_codigo,
            'Producto':prod_new,
            'Categoria':cat_new,
            'Precio':precio_new,
            'Stock':stock_new,
            'FechaIngreso':fecha_new,    
        }

        df=pd.concat([df,pd.DataFrame([nuevo_producto])],ignore_index=True)
        df.to_excel(ARCHIVO,index=False)
        st.write(nuevo_codigo)
        st.success(f'Producto registrado correctamente con el codigo:{nuevo_codigo}')

# pregunta 9

st.subheader('Consulta stock producto')

df_filtrado3 = df.copy()
busqueda = st.text_input("Buscar stock producto:", placeholder="Escribe código de producto")

if busqueda:
    df_filtrado3 = df_filtrado3[df_filtrado3["Codigo"].str.contains(busqueda, case=False)]
if not busqueda:
    st.dataframe(df.iloc[0:0])
else:
    st.dataframe(df_filtrado3)

if len(df_filtrado3) == 1:
    stock = df_filtrado3.iloc[0]['Stock']

    if stock == 0:
        st.warning("Stock agotado")
    elif stock < 5:
        st.info("Stock crítico")
    else:
        st.success("Stock disponible")

# pregunta 10

st.header('Calculos')

fecha_actual = pd.Timestamp.now()

df['ValorTotal'] = df['Precio'] * df['Stock'] 
df['MargenGanancia'] = df['Precio'] * 0.12 
df['DiasEnInventario'] = (fecha_actual - df['FechaIngreso']).dt.days

st.dataframe(df)

# pregunta 11

st.header('Gráficos')

conteo_cat= df['Categoria'].value_counts()
costo_tipo=df.groupby('Categoria')['Precio'].sum()
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,5))
ax1.bar(conteo_cat.index,conteo_cat.values)
ax1.set_title('Cantidad productos por categoria')
ax1.set_ylabel('Cantidad')
ax1.set_xticklabels(conteo_cat.index,rotation=45)
ax2.pie(costo_tipo,labels=costo_tipo.index,autopct='%1.1f%%',startangle=90)
ax2.set_title('Valor total por categoria')
plt.tight_layout()
st.write(fig)


