from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import secrets

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ✅ Use IBM Granite Model locally
tokenizer = AutoTokenizer.from_pretrained("ibm-granite/granite-3.3-2b-instruct")
model = AutoModelForCausalLM.from_pretrained("ibm-granite/granite-3.3-2b-instruct")
llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

def generate_response(prompt: str) -> str:
    system_prompt = (
        "You are a Sustainable Smart City Assistant. Your role is to help users with intelligent responses related to eco-friendly urban living.\n"
        "You support the following features:\n"
        "1. Smart Eco Tips: Provide waste management and disposal suggestions.\n"
        "2. Water Management: Analyze past usage and predict future trends.\n"
        "3. Traffic Route Analysis: Suggest optimized routes and reduce congestion.\n"
        "Be concise, clear, and use emojis where helpful.\n"
        "User query:\n"
    )
    full_prompt = system_prompt + prompt
    result = llm(full_prompt, max_new_tokens=250, temperature=0.7)
    return result[0]['generated_text']

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...), topic: str = Form(...)):
    full_prompt = f"Topic: {topic}\nQuestion: {user_input}"
    response = generate_response(full_prompt)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "response": response
    })

@app.post("/upload", response_class=HTMLResponse)
async def upload_data(request: Request, data_file: UploadFile = File(...), data_type: str = Form(...)):
    content = await data_file.read()
    decoded = content.decode("utf-8")
    map_routes = []
    chart_labels = []
    chart_values = []
    chart_type = "bar"

    if data_type == "Traffic" and "Lat1" in decoded:
        lines = decoded.strip().splitlines()[1:]  # Skip header
        routes = []
        for line in lines:
            try:
                lat1, lon1, lat2, lon2 = map(float, line.strip().split(","))
                routes.append(f"From ({lat1}, {lon1}) to ({lat2}, {lon2})")
                map_routes.append({
                    "lat1": lat1, "lon1": lon1,
                    "lat2": lat2, "lon2": lon2
                })
            except:
                continue

        coord_prompt = "\n".join(routes)
        prompt = (
            "You are a Smart City Traffic Route Assistant.\n"
            "Analyze the following coordinate-based traffic routes and suggest:\n"
            "- Shortest paths\n"
            "- Time-saving strategies\n"
            "- Avoidance of high-congestion zones\n"
            "- Alternate routes if necessary\n\n"
            f"Route Data:\n{coord_prompt}"
        )

    else:
        lines = decoded.strip().splitlines()
        header = lines[0].split(",")
        if len(header) == 2:
            for row in lines[1:]:
                try:
                    label, value = row.strip().split(",")
                    chart_labels.append(label)
                    chart_values.append(float(value))
                except:
                    continue
        if data_type == "Water":
            chart_type = "line"
        elif data_type == "Waste":
            chart_type = "pie"

        prompt = (
            f"You are analyzing {data_type} data for a Smart City.\n"
            f"Uploaded File Content:\n{decoded}\n\n"
            f"Give detailed insights, predictions, or optimization suggestions based on this {data_type.lower()} data."
        )

    response = generate_response(prompt)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "response": response,
        "map_routes": map_routes,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "chart_type": chart_type,
        "data_type": data_type
    })
