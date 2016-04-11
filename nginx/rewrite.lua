local routes = _G.routes

local function execCommand(command)
    local handle = io.popen(command,"r")
    local content = handle:read("*all")
    handle:close()
    return content
end

if routes == nil then
    routes = {}
    ngx.log(ngx.ALERT, "[[[Route cache is empty.]]")
end

local container_name = string.sub(ngx.var.http_host, 1, string.find(ngx.var.http_host, "%.")-1)
ngx.log(ngx.ALERT, "=ngx.var.http_host=[["..ngx.var.http_host.."]]==")
ngx.log(ngx.ALERT, "==container-name==[[["..container_name.."]]")

local route = routes[container_name]
if route == nil then
    local Redis  = require "nginx.redis"
    local client = Redis:new()

    client:set_timeout(1000)
    local ok, err = client:connect("127.0.0.1", 6379)
    if not ok then
        ngx.log(ngx.ERR, "************ Redis connection failure: " .. err)
        return
     end

    -- (test data regist sample)
    --client:set(ngx.var.http_host,"172.17.0.5:8080")

    route = client:get(container_name)
end

ngx.log(ngx.ALERT, route)

-- fallback to redis for lookups
if (type(route) == "string") then
    ngx.log(ngx.ALERT, "=ok=[["..route.."]]===")
    ngx.var.upstream = route
    routes[container_name] = route
    --(docker container is no cache)
    --_G.routes = routes
else
    nexthost = execCommand("hostbyaddress $(nexthost)")
    ngx.log(ngx.ALERT, "=next-redirect=[[["..nexthost.."]]]")
    ngx.var.upstream = nexthost
    routes[container_name] = route
end
