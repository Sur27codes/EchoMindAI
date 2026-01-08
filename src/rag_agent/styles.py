def get_custom_css():
    """Returns the premium custom CSS for EchoMindAI."""
    return """
    </style>
    
    </style>
    
    <script>
    (function() {
        console.log("Initializing Neon Particle Sandbox...");
        
        // 1. Setup Canvas
        const canvas = document.createElement('canvas');
        canvas.id = 'neon-sandbox-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '0'; // Behind everything
        canvas.style.pointerEvents = 'none'; // Click through to UI
        
        // Remove old if exists
        const existing = document.getElementById('neon-sandbox-canvas');
        if (existing) existing.remove();
        
        document.body.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        
        let width, height;
        
        // 2. Physics Configuration
        const CONFIG = {
            particleCount: 150,
            connectionDistance: 100,
            mouseRadius: 200,
            friction: 0.95,
            colors: ['#FF61D2', '#5C24FF', '#00EAFF', '#FFFFFF']
        };

        // 3. State
        let particles = [];
        let mouse = { x: -1000, y: -1000, active: false };
        
        function resize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            initParticles();
        }
        window.addEventListener('resize', resize);
        
        // 4. Mouse Tracking (Global)
        document.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
            mouse.active = true;
        });

        // Click Explosion Effect
        document.addEventListener('mousedown', (e) => {
            explode(e.clientX, e.clientY);
        });

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = (Math.random() - 0.5) * 2;
                this.size = Math.random() * 2 + 1;
                this.color = CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)];
                this.origSize = this.size;
            }
            
            update() {
                // Physics
                this.x += this.vx;
                this.y += this.vy;
                
                // Mouse Interaction / "Play" Logic
                if (mouse.active) {
                    const dx = mouse.x - this.x;
                    const dy = mouse.y - this.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < CONFIG.mouseRadius) {
                        // Repel / Swirl effect
                        const forceDirectionX = dx / dist;
                        const forceDirectionY = dy / dist;
                        const force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius;
                        
                        // Push away gently
                        const dir = -1; // -1 = repel, 1 = attract
                        this.vx += forceDirectionX * force * dir * 1.5;
                        this.vy += forceDirectionY * force * dir * 1.5;
                        
                        // Grow size when near mouse
                        this.size = Math.min(this.origSize * 3, this.size + 0.2); 
                    } else {
                        if (this.size > this.origSize) this.size -= 0.1;
                    }
                }
                
                // Friction for control
                this.vx *= CONFIG.friction;
                this.vy *= CONFIG.friction;
                
                // Keep moving a bit
                const minSpeed = 0.5;
                if (Math.abs(this.vx) < minSpeed && Math.abs(this.vy) < minSpeed) {
                     this.vx += (Math.random() - 0.5) * 0.2;
                     this.vy += (Math.random() - 0.5) * 0.2;
                }
                
                // Wrap around screen
                if (this.x < 0) this.x = width;
                if (this.x > width) this.x = 0;
                if (this.y < 0) this.y = height;
                if (this.y > height) this.y = 0;
            }
            
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }
        
        function initParticles() {
            particles = [];
            for (let i = 0; i < CONFIG.particleCount; i++) {
                particles.push(new Particle());
            }
        }
        
        function explode(x, y) {
            // Push all nearby particles away drastically
            for (let p of particles) {
                const dx = p.x - x;
                const dy = p.y - y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                
                if (dist < 400) {
                    const angle = Math.atan2(dy, dx);
                    const force = 20; // Explosion force
                    p.vx = Math.cos(angle) * force;
                    p.vy = Math.sin(angle) * force;
                }
            }
        }
        
        function animate() {
            ctx.clearRect(0, 0, width, height);
            
            // Draw connections first
            ctx.lineWidth = 0.5;
            for (let i = 0; i < particles.length; i++) {
                const p1 = particles[i];
                // Check neighbors
                // Optimization: only check a subset or grid (skipping for simplicity here)
                // We'll limit checks to keep FPS high
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y; 
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < CONFIG.connectionDistance) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(100, 100, 255, ${1 - dist/CONFIG.connectionDistance})`;
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
                p1.update();
                p1.draw();
            }
            requestAnimationFrame(animate);
        }
        
        // Start
        
        resize();
        animate();
        
        // --- 5. React-Like Interactions (Lightbox & Scroll Observer) ---
        
        // LIGHTBOX for Images
        const lightbox = document.createElement('div');
        lightbox.id = 'img-lightbox';
        Object.assign(lightbox.style, {
            position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
            backgroundColor: 'rgba(0,0,0,0.9)', zIndex: 10000,
            display: 'none', alignItems: 'center', justifyContent: 'center',
            cursor: 'zoom-out', backdropFilter: 'blur(5px)'
        });
        const lbImg = document.createElement('img');
        Object.assign(lbImg.style, { maxHeight: '90%', maxWidth: '90%', borderRadius: '8px', boxShadow: '0 0 50px rgba(0,0,0,0.5)' });
        lightbox.appendChild(lbImg);
        document.body.appendChild(lightbox);
        
        lightbox.onclick = () => { lightbox.style.display = 'none'; };
        
        // Event Delegation for dynamically added images
        document.body.addEventListener('click', (e) => {
            if (e.target.tagName === 'IMG' && e.target.closest('.product-card-img-container')) {
                lbImg.src = e.target.src;
                lightbox.style.display = 'flex';
            }
        });
        
        // SCROLL REVEAL OBSERVER
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target); // Once only
                }
            });
        }, { threshold: 0.1 });
        
        // Continuously observe new elements
        setInterval(() => {
            document.querySelectorAll('.product-card:not(.observed), .glass-card:not(.observed)').forEach(el => {
                el.classList.add('observed', 'hidden-state');
                observer.observe(el);
            });
        }, 1000); // Check every second
        
    })();
    </script>
    
    <style>
        /* Animation States */
        .hidden-state {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease-out, transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        
        .visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            /* Friendly Vibrant Palette */
            --bg-base: #111111;
            --bg-sidebar: rgba(20, 20, 20, 0.6);
            --bg-card: rgba(255, 255, 255, 0.05);
            --bg-input: rgba(255, 255, 255, 0.1);
            
            --text-primary: #FFFFFF;
            --text-secondary: #E0E0E0;
            
            --border-glass: 1px solid rgba(255, 255, 255, 0.4);
            --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            
            --radius-lg: 24px;
            --radius-md: 16px;
        }
        
        /* Interactive Neon Aura */
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            /* Colorful moving orb tracking mouse */
            background: radial-gradient(
                600px circle at var(--x, 50vw) var(--y, 50vh), 
                rgba(255, 60, 255, 0.1),
                rgba(92, 36, 255, 0.1),
                transparent 50%
            );
            /* Add a second layer for depth */
            box-shadow: inset 0 0 100px rgba(0,0,0,0.5);
            z-index: -1;
            pointer-events: none;
            mix-blend-mode: screen; /* Helps colors pop without washing out black */
        }       
        
        /* Fun floating particles animation (simulated via background) */
        @keyframes float-bg {
             0% { background-position: 0% 0%; }
             50% { background-position: 20% 50%; }
             100% { background-position: 0% 0%; }
        }

        .stApp {
            background-color: var(--bg-base);
        .stApp {
            background-color: var(--bg-base);
            /* Deep Dark Space Background */
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(20, 0, 40, 0.3) 0%, transparent 25%), 
                radial-gradient(circle at 85% 30%, rgba(40, 0, 60, 0.2) 0%, transparent 25%), 
                linear-gradient(180deg, #020202 0%, #080808 100%);
            background-size: 100% 100%;
            /* No animation needed for solid dark, or a very subtle pulse */
            
            font-family: 'Outfit', sans-serif;
            color: var(--text-primary);
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.01em;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        code {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-sidebar);
            border-right: var(--border-glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }

        /* Glass Cards */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-glass);
            margin-bottom: 20px;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.08); /* Light up on hover */
        }

        /* Hero Text Gradient */
        .gradient-text {
            background: linear-gradient(135deg, #FF61D2 0%, #FE9090 50%, #5C24FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline-block;
            filter: drop-shadow(0 0 10px rgba(255, 97, 210, 0.3));
        }

        /* Chat Bubbles */
        .stChatMessage { background: transparent; }
        
        /* User Bubble */
        div[data-testid="stChatMessage"][data-testid="stChatMessage-user"] div[data-testid="stChatMessageContent"] {
            background: linear-gradient(135deg, rgba(92, 36, 255, 0.4) 0%, rgba(255, 59, 255, 0.2) 100%);
            border: var(--border-glass);
            backdrop-filter: blur(12px);
            border-radius: 20px 20px 4px 20px !important;
            padding: 16px 24px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* Assistant Bubble */
        div[data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] div[data-testid="stChatMessageContent"] {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-left: 3px solid #FF61D2;
            border-radius: 4px 20px 20px 20px !important;
            padding: 16px 24px !important;
            color: #FFFFFF !important; /* Force white text */
        }
        
        /* Ensure all nested text elements are white */
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] li {
            color: #FFFFFF !important;
        }

        /* Buttons */
        div.stButton > button {
            background: rgba(255, 255, 255, 0.08);
            border: var(--border-glass);
            color: var(--text-primary);
            border-radius: var(--radius-md);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }
        
        /* --- PREMIUM GLASSMORPHISM BUTTONS --- */
        div.stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.05); /* Ultra-sheer glass */
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        div.stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            color: #fff;
        }
        
        div.stButton > button:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: white;
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 97, 210, 0.4);
        }
        
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #FF61D2, #5C24FF);
            border: none;
            color: #fff;
            font-weight: 600;
        }

        /* Gradient Text Animation for Title */
        h1 span {
            background: linear-gradient(to right, #FF61D2, #FE9090, #5C24FF, #00D4FF);
            background-size: 300% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 5s linear infinite;
        }

        @keyframes shine {
            to {
                background-position: 200% center;
            }
        }

        /* --- IMMERSIVE CHAT BAR (AGGRESSIVE REMOVAL) --- */
        
        /* 1. Hide Header/Footer fully */
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; display: none !important; }
        
        /* 2. Target the exact bottom container Streamlit uses */
        .stBottom, div[data-testid="stBottom"] {
            background: rgba(20, 20, 20, 0.7) !important; /* Semi-transparent dark */
            backdrop-filter: blur(20px) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
            box-shadow: 0 -10px 30px rgba(0,0,0,0.5) !important;
            padding-top: 15px !important;
            padding-bottom: 20px !important;
        }
        
        /* 3. Target any children wrapper divs that might hold color */
        /* 3. Target any children wrapper divs that might hold color */
        .stBottom > div {
             background: transparent !important;
        }
        
        /* 4. Force the main app container to span full height and show background */
        /* 4. Force the main app container to span full height and show background */
        .stApp {
            background-color: transparent !important; /* Let body bg show through */
        }
        
        /* 5. The Chat Input container itself - The "White Box" culprit */
        /* Aggressively target the wrapper to remove the faint white edge */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] * {
             background-color: transparent !important;
             background: transparent !important;
             box-shadow: none !important;
             border: none !important;
             outline: none !important;
        }
        
        /* Restore the specific input styling that we DO want */
        .stChatInput textarea {
            background-color: rgba(20, 20, 20, 0.8) !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important; /* Subtle border */
        }
        
        /* Placeholder color */
        .stChatInput textarea::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }
        
        
        /* Remove the default red border on focus and replace with subtle white glow */
        .stChatInput textarea:focus,
        .stChatInput textarea:focus-visible {
            border-color: rgba(255, 255, 255, 0.4) !important;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.1) !important;
            outline: none !important;
        }

        /* Target the specific red-border element Streamlit adds (internal classes) */
        div[data-testid="stChatInput"] > div {
            border-color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }
        
        /* Specific override for the active container */
        .st-emotion-cache-1h9usn1, .st-emotion-cache-12fmw14, .st-emotion-cache-1dp5vir {
            border-color: transparent !important;
            box-shadow: none !important;
        }


        /* Remove default streamlit rounded styling from the wrapper */
        [data-testid="stChatInput"] {
            border-radius: 0 !important;
        }
        
        /* Just the Input Box itself should have style */
        .stChatInputContainer {
             padding-bottom: 20px;
        }
        
        /* PREMIUM GLASS PILL INPUT */
        .stChatInput textarea {
            background-color: rgba(20, 20, 20, 0.8) !important; /* Dark solid base */
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 30px !important;
            color: white !important;
            caret-color: #FF61D2 !important;
            padding: 12px 20px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        }
        
        .stChatInput textarea:focus {
            border-color: #FF61D2 !important;
            box-shadow: 0 0 15px rgba(255, 97, 210, 0.3) !important;
            background-color: rgba(0, 0, 0, 0.9) !important;
        }
        
        .stChatInput textarea::placeholder {
            color: rgba(200, 200, 200, 0.6) !important;
        }
        
        /* Submit Button */
        .stChatInput button {
            color: #FF61D2 !important;
        }
        
        /* Generic Input Fields */
        .stTextInput input {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            color: white !important;
            border-radius: 12px !important; 
        }

        /* Fun Glow Animation */
        @keyframes subtle-float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .hero-title {
            animation: subtle-float 3s ease-in-out infinite;
        }

        /* File Uploader Fix */
        [data-testid="stFileUploader"] {
            background-color: rgba(255,255,255,0.02);
            border: 1px dashed rgba(255,255,255,0.4);
            border-radius: var(--radius-md);
            padding: 15px;
        }
        
        [data-testid="stFileUploader"] section { background: transparent !important; }
        [data-testid="stFileUploader"] div[data-testid="stFileUploaderFile"] { background: rgba(255,255,255,0.1) !important; }

        /* Hide Streamlit Elements */
        #MainMenu, footer, .stDeployButton { display: none; }

    /* --- Premium Table Styles --- */
    table {
        width: 100%;
        border-collapse: separate; 
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        margin: 20px 0;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    th {
        background: rgba(255, 255, 255, 0.08);
        color: #FF61D2 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: #EEEEEE;
        vertical-align: middle;
    }
    
    td img {
        border-radius: 8px;
        max-height: 100px;
        width: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    
    td img:hover {
        transform: scale(1.1);
        z-index: 10;
    }

    tr:last-child td {
        border-bottom: none;
    }
    
    tr:hover td {
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Ensure code blocks don't ruin tables if they accidentally appear */
    table code {
        background: rgba(0,0,0,0.3);
        color: #FF61D2;
        padding: 2px 6px;
        border-radius: 4px;
    }

    /* --- PRODUCT CARDS (GRID LAYOUT) --- */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .product-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
        backdrop-filter: blur(10px);
    }

    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(92, 36, 255, 0.3);
        border-color: rgba(255, 97, 210, 0.5);
        z-index: 10;
        background: rgba(255, 255, 255, 0.08);
    }

    .product-card-img-container {
        width: 100%;
        height: 180px;
        background: rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .product-card img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    
    .product-card:hover img {
        transform: scale(1.05);
    }

    .product-card-content {
        padding: 16px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }

    .product-card h3 {
        margin: 0 0 8px 0;
        font-size: 1.1rem;
        font-weight: 600;
        line-height: 1.4;
        color: white;
    }

    .product-card .price {
        font-size: 1.25rem;
        color: #FF61D2;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .product-card .rating {
        color: #FFD700;
        font-size: 0.9rem;
        margin-bottom: 12px;
        font-weight: 500;
    }
    
    .product-card .description {
        font-size: 0.85rem;
        color: #B0B0B0;
        margin-bottom: 16px;
        flex-grow: 1;
        line-height: 1.5;
    }

    .product-card .action-btn {
        display: block;
        text-align: center;
        background: linear-gradient(90deg, #FF61D2 0%, #5C24FF 100%);
        color: white !important;
        text-decoration: none;
        padding: 10px;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity 0.2s;
        margin-top: auto; /* Push to bottom */
    }

    .product-card .action-btn:hover {
        opacity: 0.9;
        text-decoration: none;
    }

    /* Fallback image style handled by JS/HTML error, but basic styling here */
    .img-error {
        padding: 20px;
        color: #666;
        font-size: 0.8rem;
    }
        
    </style>
    """

