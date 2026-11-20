-- Minimal in-game panel for the Java bridge.
PZMapStudioPanel = ISPanel:derive("PZMapStudioPanel")

function PZMapStudioPanel:new(x, y, w, h)
    local o = ISPanel.new(self, x, y, w, h)
    o.backgroundColor = {r=0.04, g=0.06, b=0.05, a=0.92}
    o.borderColor = {r=0.35, g=0.55, b=0.35, a=1}
    o.lines = {}
    return o
end

function PZMapStudioPanel:createChildren()
    ISPanel.createChildren(self)
    local close = ISButton:new(self.width - 90, self.height - 34, 80, 26, "Close", self, PZMapStudioPanel.close)
    close:initialise()
    close:instantiate()
    self:addChild(close)
end

function PZMapStudioPanel:close()
    self:setVisible(false)
    self:removeFromUIManager()
end

function PZMapStudioPanel:setLines(lines)
    self.lines = lines or {}
end

function PZMapStudioPanel:render()
    ISPanel.render(self)
    self:drawText("PZMapStudio", 12, 10, 0.9, 1, 0.85, 1, UIFont.Medium)
    local y = 40
    for _, line in ipairs(self.lines) do
        self:drawText(tostring(line), 12, y, 0.85, 0.9, 0.85, 1, UIFont.Small)
        y = y + 18
    end
end

local function openPanel()
    if not PZMapStudioPanel.instance then
        PZMapStudioPanel.instance = PZMapStudioPanel:new(
            getCore():getScreenWidth() / 2 - 300,
            getCore():getScreenHeight() / 2 - 180,
            600, 360)
        PZMapStudioPanel.instance:initialise()
        PZMapStudioPanel.instance:addToUIManager()
    end
    local lines = {}
    if PZMapStudioAPI then
        local api = PZMapStudioAPI.getInstance()
        table.insert(lines, api:status())
        table.insert(lines, api:help())
    else
        table.insert(lines, "Java API not loaded.")
        table.insert(lines, "Approve PZMapStudio.jar in ZombieBuddy if prompted.")
    end
    PZMapStudioPanel.instance:setLines(lines)
    PZMapStudioPanel.instance:setVisible(true)
end

local function togglePanel()
    if PZMapStudioPanel.instance and PZMapStudioPanel.instance:isVisible() then
        PZMapStudioPanel.instance:close()
    else
        openPanel()
    end
end

Events.OnKeyPressed.Add(function(key)
    if key == Keyboard.KEY_F10 then
        togglePanel()
    end
end)
