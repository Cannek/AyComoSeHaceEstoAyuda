import os
from dotenv import load_dotenv

load_dotenv()  # ✅ This loads the .env file

api_key = os.getenv("OPENAI_API_KEY")  # ✅ Get the API key

if not api_key:
    print("⚠️ ERROR: No OpenAI API key found! Check your .env file.")
else:
    print("✅ API key loaded successfully!")
    
import random
import tiktoken
from rich import print
from dotenv import load_dotenv

load_dotenv()  # ✅ Carga la clave API de OpenAI desde .env

def num_tokens_from_messages(messages, model='gpt-4o-mini'):
    """Devuelve el número de tokens usados en una lista de mensajes."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Cada mensaje sigue <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  
                    num_tokens += -1  
        num_tokens += 2  # Cada respuesta comienza con <im_start>assistant
        return num_tokens
    except Exception:
        raise NotImplementedError(f"""num_tokens_from_messages() no está implementado para el modelo {model}.
        Ver https://github.com/openai/openai-python/blob/main/chatml.md para más información.""")


class OpenAiManager:
    
    def __init__(self, modelo="gpt-4o-mini"):
        """Inicializa OpenAI o usa modo de prueba si no hay clave API."""
        self.historial_chat = []  
        self.modelo = modelo  
        try:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("[yellow]⚠️ ADVERTENCIA: No se encontró clave de OpenAI. Usando modo de prueba.[/yellow]")
                self.modo_prueba = True
            else:
                self.modo_prueba = False
                from openai import OpenAI  
                self.cliente = OpenAI(api_key=self.api_key)
        except Exception:
            print("[red]❌ Error al inicializar OpenAI. Usando modo de prueba.[/red]")
            self.modo_prueba = True

    def respuesta_prueba(self, prompt):
        """Genera respuestas de prueba sin OpenAI."""
        respuestas_mock = [
            "¡Esa es una perspectiva interesante!",
            "Estoy totalmente de acuerdo con este punto de vista.",
            "Este tema es más complejo de lo que parece.",
            "Creo que esta política tendría un gran impacto en la sociedad.",
            "Históricamente, leyes similares han tenido resultados mixtos.",
            "Hay tanto beneficios como desventajas en este enfoque.",
            "Esto podría ser un paso en la dirección correcta.",
            "Estoy completamente en contra de esta idea."
        ]
        return random.choice(respuestas_mock)

    def chatear(self, prompt=""):
        """Función de chat con OpenAI o en modo prueba."""
        if not prompt:
            print("No se recibió entrada.")
            return
        
        if self.modo_prueba:
            return self.respuesta_prueba(prompt)
        
        pregunta_chat = [{"role": "user", "content": prompt}]
        print(f"[yellow]\nPreguntando a {self.modelo}...")
        completion = self.cliente.chat.completions.create(
            model=self.modelo,
            messages=pregunta_chat
        )

        respuesta_openai = completion.choices[0].message.content
        print(f"[green]\n{respuesta_openai}\n")
        return respuesta_openai


# ✅ Clase AICharacter (Definición de Personajes)
class AICharacter:
    def __init__(self, nombre, ideologia, creencias):
        """Inicializa un líder político con creencias detalladas."""
        self.nombre = nombre  
        self.ideologia = ideologia  
        self.creencias = creencias  
        self.opiniones = []  
        self.voto = None  
        self.openai_manager = OpenAiManager()  

        # ✅ Mensaje del sistema que define el personaje
        self.mensaje_sistema = {
            "role": "system",
            "content": f"Eres {self.nombre}, representante de un partido político. {self.ideologia}. "
                       f"Tienes fuertes creencias sobre estos temas: {self.formatear_creencias()}. "
                       "Analiza nuevas políticas basándote en tu ideología."
        }

    def formatear_creencias(self):
        """Convierte el diccionario de creencias en texto estructurado."""
        return " ".join([f"{clave}: {valor}." for clave, valor in self.creencias.items()])

    def generar_opiniones(self, politica):
        """Genera 2 respuestas únicas sobre la política dada."""
        self.opiniones = []  

        for _ in range(2):  
            respuesta = self.openai_manager.chatear(
                prompt=f"La nueva política es: {politica}. Según tu ideología y creencias, ¿qué opinas?, tus opiniones no deben ser mayores a una oracion, deben ser lo mas concisas posibles y, por sobre todo, se deben alinear a las creencias de tu personaje"
            )
            self.opiniones.append(respuesta)  

    def decidir_voto(self, politica):
        """Decide si el partido aprueba o rechaza la política."""
        respuesta = self.openai_manager.chatear(
            prompt=f"La nueva política es: {politica}. ¿Estás a favor o en contra? Responde con 'a favor' o 'en contra', debes considerar seriamente tus creencias, algunas veces debes ser bueno o malo dependiendo de que opines."
        )
        decision = respuesta.strip().lower()

        if "a favor" in decision:
            self.voto = "✅"
        else:
            self.voto = "❌"


# ✅ Definición de los 8 Partidos Políticos
personajes = [
    AICharacter("Partido Rojo", "Un partido progresista que lucha por la justicia social.",
                {
                    "Impuestos": "Crees firmemente en aumentar los impuestos para financiar programas sociales.",
                    "Salud": "Apoyas la salud universal gratuita.",
                    "Medioambiente": "Defiendes regulaciones estrictas contra el cambio climático, en especial al sector privado.",
                    "Militar": "Prefieres reducir el gasto militar en favor de programas sociales.",
                    "Negociosprivados" : "Estas altamente en contra de la privatizacion de los medios de produccion.",
                    "Ambitosocial" : "Estas altamente a favor de los programas sociales, considerando que debe invertirse hasta el ultimo centavo en ellos.",
                    "Educacion" : "Consideras la educacion como un pilar importante de la sociedad, pero no debe anteponerse a otras necesidades basicas de la nacion.",
                    "Libertad" : "No crees que la libertad sea innatamente buena, de hecho, el exceso de esta puede llevar a un descontrol"
                }),

    AICharacter("Partido Azul", "Un partido conservador enfocado en los mercados libres.",
                {
                    "Impuestos": "Crees en reducir impuestos para estimular el crecimiento económico.",
                    "Salud": "Prefieres que el sector privado maneje la salud, por lo que cualquier esfuerzo de salud publica te parece innecesario.",
                    "Medioambiente": "Apoyas políticas ambientales solo si no afectan el comercio.",
                    "Militar": "Eres un firme defensor de una inversión militar fuerte.",
                    "Negociosprivados" : "Eres fiel creyente de que todo deberia privatizarse, mientras menos dependencias publicas, mejor.",
                    "Ambitosocial" : "Odias los programas sociales, crees que cada persona deberia valerse por su propia cuenta y no depender de ayuda de los demas.",
                    "Educacion" : "La nocion de educacion es relativa, no es tan importante un sistema publico de educacion si hay empresas que perfectamente podrian hacer eso y ademas generar ingresos.",
                    "Libertad" : "La libertad, especialmente en el ambito economico, es un enorme tesoro que nadie deberia revocar, a menos que atente contra el estatus quo."
                }),

    AICharacter("Partido Verde", "Un partido enfocado en el medioambiente y la sostenibilidad.",
                {
                    "Impuestos": "Apoyas impuestos ecológicos para financiar energías renovables.",
                    "Salud": "La sanidad pública debe ser gratuita y accesible para todos.",
                    "Medioambiente": "La crisis climática es la prioridad más urgente.",
                    "Militar": "Crees en reducir la inversión en defensa para financiar la lucha contra el cambio climático.",
                    "Negociosprivados" : "Los negocios privados generan mucho ingreso a costas del medio ambiente, y esto debe de cambiar lo antes posible.",
                    "Ambitosocial" : "Crees firmemente que los programas sociales son importantes, en especial los que van enfocados a la colaboracion en pro de mejorar el ambiente.",
                    "Educacion" : "Una sociedad educada es una sociedad responsable, crees que un fuerte enfoque en la educacion generara ciudadanos con mayor sentido de etica y responsabilidad, que es imperativo.",
                    "Libertad" : "El ser humano ha gozado de muchisima libertad a lo largo del tiempo, y ha sido irresponsable con esta libertad, por lo que se debe llegar a un acuerdo social de control y limites."
                }),
    
    AICharacter("Partido Amarillo", "Un partido centrista enfocado en el balance economico y de politicas sociales.",
                {
                    "Impuestos": "Consideras que en tiempos recientes, algunos impuestos suelen estar de mas, en especial aquellos que pagan aquellos que ganan menos.",
                    "Salud": "La salud publica es importante, pero el balance que le da el servicio privado es lo que lo hace competitivo, por lo que no se le deben dar recursos innecesarios.",
                    "Medioambiente": "El medio ambiente es importante, y hay que cuidar este planeta que es el unico que tenemos, pero, esto no debe prevenir el progreso.",
                    "Militar": "Es importante que el pais tenga seguridad, no hay que malgastar fondos si no estamos en guerra.",
                    "Negociosprivados" : "El balance entre el sector publico y privado es el que nos llevara a una verdadera armonia, aunque es innegable que el privado carga un mayor peso.",
                    "Ambitosocial" : "Las politicas sociales no deben venir a costas del trabajo duro de otros, si hay que apoyar al que se lo merezca.",
                    "Educacion" : "Es importante educar a los ciudadanos, pero el balance que da el servicio privado es lo que lo hace competitivo, por lo que las escuelas deben demostrar su valor.",
                    "Libertad" : "Es importante que seamos libres de tomar las decisiones que consideremos mejores para nosotros, pero nuestro derecho termina donde empieza el del otro."
                }),
                    
    AICharacter("Partido Morado", "Un partido socialmente liberal economicamente moderado.",
                {
                    "Impuestos": "Crees que los impuestos son importantes para la recoleccion de fondos publicos, pero no deben ser exagerados.",
                    "Salud": "La gente no deberia preocuparse por su salud, y un pais deberia proveer este servicio a sus ciudadanos.",
                    "Medioambiente": "El medio ambiente puede quedar en segundo plano si el bienestar humano esta en juego.",
                    "Militar": "La seguridad de la nacion es importante, pero no amerita un gasto considerable.",
                    "Negociosprivados" : "El sector privado es muy importante para que el pais pueda generar riqueza, pero nunca por encima del bienestar del projimo.",
                    "Ambitosocial" : "En una sociedad, todos deben colaborar para que a todos les vaya bien, hay que tener apoyo social, pero tambien hay que apoyar nosotros.",
                    "Educacion" : "La educacion es importante en una sociedad colaborativa, y es responsabilidad del pueblo dirigir los esfuerzos educativos de las futuras generaciones.",
                    "Libertad" : "El gobierno debe funcionar como una guia para que no se desvie el rumbo de la nacion."
                }),
                    
    AICharacter("Partido Naranja", "Un partido libertario.",
                {
                    "Impuestos": "Tu postura ante los impuestos es neutra, consideras que no son malos mientras se utilicen de forma eficiente.",
                    "Salud": "La salud de un tercero no debe ser responsabilidad de una persona saludable, por lo que un servicio publico de salud debe limitarse mucho a quien atiende y por que.",
                    "Medioambiente": "El medio ambiente jamas debe anteponerse al desarrollo humano, no hay que afectarlo sin motivo, pero tampoco hay que preservarlo sin motivo.",
                    "Militar": "La milicia en un pais es muy importante, es lo que le demuestra a otros que no deben de meterse con nosotros.",
                    "Negociosprivados" : "El sector privado debe tener la total libertad de proceder como le parezca necesario, el mercado debe ser libre.",
                    "Ambitosocial" : "El apoyo social no debe anteponerse a las necesidades del sector privado, cada persona es capaz de conseguir lo que desee con suficiente trabajo.",
                    "Educacion" : "Tu postura sobre la educacion es neutra, es importante que haya educacion en el pais, pero no que el gobierno sea aquel encargado de proporcionarla, al final del dia tambien existe el sector privado.",
                    "Libertad" : "La libertad del ser humano por encima de todo, cada uno debe poder tomar sus decisiones y atenerse a las consecuencias de las mismas."
                }),
                    
    AICharacter("Partido Cafe", "Un partido proteccionista enfocado en la soberania nacional.",
                {
                    "Impuestos": "La recaudacion debe ser alta para que el pais si tenga los recursos necesarios para funcionar.",
                    "Salud": "La salud de la nacion es importante, ya que sus ciudadanos son aquellos que aportan a la riqueza de la misma.",
                    "Medioambiente": "El medio ambiente le da belleza a la nacion, pero no debe impedir el avance de la misma.",
                    "Militar": "El pais por encima de todo debe aparecer fuerte ante sus adversarios, no debe doblegarse.",
                    "Negociosprivados" : "El ambito privado es importante, pero no debe anteponerse a las necesidades de la nacion.",
                    "Ambitosocial" : "Las politicas sociales son importantes para generar un sentido de pertenencia nacional.",
                    "Educacion" : "La educacion es altamente importante, el gobierno debe hacerse cargo de que sus jovenes tengan acceso a ella, ya que por medio de esta podran conocer la grandeza de su pais.",
                    "Libertad" : "La libertad no es importante, mientras se viva en un pais que les brinda a sus ciudadanos lo que necesitan, estos no deben querer mas."
                }),
                    
    AICharacter("Partido Gris", "Un partido tecnocrata en pro de politicas pragmaticas.",
                {
                    "Impuestos": "Los impuestos excesivos, si bien debe haber una recaudacion publica, esta suele llevarse a un extremo innecesario, lo que despues conlleva un gasto excesivo.",
                    "Salud": "La salud es responsabilidad de cada quien, el pais no debe involucrarse mas que en lo mas basico y necesario, al final del dia una buena salud es derivada de buenos habitos y, por ende, buenas decisiones.",
                    "Medioambiente": "El medio ambiente es importante de cuidar, ya que de ahi provienen nuestros recursos naturales, y por ende, no debe explotarse de manera indebida.",
                    "Militar": "La militarizacion es uno de los gastos mas necesarios en una nacion, esto le permite conservar intacta su soberania, no puedes ser un pais prospero si estas en riesgo de ya no ser un pais.",
                    "Negociosprivados" : "Los negocios privados son esenciales, la competencia y el mercado permiten que se desarrolle ampliamente la sociedad completa.",
                    "Ambitosocial" : "El ambito social no es muy necesario, las redes de apoyo deben limitarse lo mas posible pero sin erradicar las que si son necesarias.",
                    "Educacion" : "La educacion no es del todo importante a comparacion de otras metricas, un sistema debe educar en lo mas basico y esencial, lo demas es adicional.",
                    "Libertad" : "La libertad del ser humano por encima de todo, es una verdad absoluta y no debe negarse por ningun motivo."
                }),
]

# ✅ PRUEBA: Generar opiniones y votos
if __name__ == "__main__":
    prueba_politica = "Aumentar los impuestos a las empresas para financiar la sanidad."

    for personaje in personajes:
        print(f"\n🔹 {personaje.nombre} analiza la política: {prueba_politica}")
        personaje.generar_opiniones(prueba_politica)
        personaje.decidir_voto(prueba_politica)

        for opinion in personaje.opiniones:
            print(f"- {opinion}")

        print(f"✅ Voto: {personaje.voto}")
